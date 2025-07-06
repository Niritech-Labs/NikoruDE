//Copyright (C) 2024-2025 Niritech Labs
//This program is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#include <iostream>
#include <stdexcept>
#include <vector>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <libdrm/drm.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

class DRMResolutionManager {
public:
    DRMResolutionManager() : fd(-1) {}

    ~DRMResolutionManager() {
        close_drm();
    }

    bool open_drm() {
        for (int i = 0; i < 8; i++) {
            std::string path = "/dev/dri/card" + std::to_string(i);
            fd = open(path.c_str(), O_RDWR);
            if (fd >= 0) {
                std::cout << "Opened DRM device: " << path << std::endl;
                return true;
            }
        }

        fd = drmOpen(nullptr, nullptr);
        if (fd < 0) {
            throw std::runtime_error("drmOpen failed");
        }
        std::cout << "Opened DRM device via drmOpen" << std::endl;
        return true;
    }

    void close_drm() {
        if (fd >= 0) {
            close(fd);
            fd = -1;
            std::cout << "Closed DRM device" << std::endl;
        }
    }

    std::pair<int, int> get_current_resolution() {
        if (fd < 0 && !open_drm()) {
            throw std::runtime_error("Failed to open DRM device");
        }

        drmModeRes* res = drmModeGetResources(fd);
        if (!res) {
            throw std::runtime_error("drmModeGetResources failed");
        }

        drmModeConnector* connector = find_active_connector(res);
        if (!connector) {
            drmModeFreeResources(res);
            throw std::runtime_error("No active connector found");
        }

        drmModeEncoder* encoder = drmModeGetEncoder(fd, connector->encoder_id);
        if (!encoder) {
            drmModeFreeConnector(connector);
            drmModeFreeResources(res);
            throw std::runtime_error("drmModeGetEncoder failed");
        }

        drmModeCrtc* crtc = drmModeGetCrtc(fd, encoder->crtc_id);
        if (!crtc) {
            drmModeFreeEncoder(encoder);
            drmModeFreeConnector(connector);
            drmModeFreeResources(res);
            throw std::runtime_error("drmModeGetCrtc failed");
        }

        int width = crtc->width;
        int height = crtc->height;

        drmModeFreeCrtc(crtc);
        drmModeFreeEncoder(encoder);
        drmModeFreeConnector(connector);
        drmModeFreeResources(res);

        return std::make_pair(width, height);
    }

    bool set_resolution(int width, int height, int refresh = 60) {
        if (fd < 0 && !open_drm()) {
            throw std::runtime_error("Failed to open DRM device");
        }

        drmModeRes* res = drmModeGetResources(fd);
        if (!res) {
            throw std::runtime_error("drmModeGetResources failed");
        }

        drmModeConnector* connector = find_active_connector(res);
        if (!connector) {
            drmModeFreeResources(res);
            throw std::runtime_error("No active connector found");
        }

        drmModeModeInfo* mode = find_matching_mode(connector, width, height, refresh);
        if (!mode) {
            drmModeFreeConnector(connector);
            drmModeFreeResources(res);
            throw std::runtime_error("No matching mode found");
        }

        drmModeEncoder* encoder = drmModeGetEncoder(fd, connector->encoder_id);
        if (!encoder) {
            drmModeFreeConnector(connector);
            drmModeFreeResources(res);
            throw std::runtime_error("drmModeGetEncoder failed");
        }

        // Получаем текущий CRTC
        drmModeCrtc* crtc = drmModeGetCrtc(fd, encoder->crtc_id);
        if (!crtc) {
            drmModeFreeEncoder(encoder);
            drmModeFreeConnector(connector);
            drmModeFreeResources(res);
            throw std::runtime_error("drmModeGetCrtc failed");
        }

        // Устанавливаем новый режим
        int ret = drmModeSetCrtc(fd, crtc->crtc_id, crtc->buffer_id, 
                                 crtc->x, crtc->y, 
                                 &connector->connector_id, 1, 
                                 mode);
        
        drmModeFreeCrtc(crtc);
        drmModeFreeEncoder(encoder);
        drmModeFreeConnector(connector);
        drmModeFreeResources(res);

        if (ret != 0) {
            throw std::runtime_error("drmModeSetCrtc failed: " + std::string(strerror(-ret)));
        }

        return true;
    }

private:
    int fd;

    drmModeConnector* find_active_connector(drmModeRes* res) {
        for (int i = 0; i < res->count_connectors; i++) {
            drmModeConnector* connector = drmModeGetConnector(fd, res->connectors[i]);
            if (connector) {
                if (connector->connection == DRM_MODE_CONNECTED) {
                    return connector;
                }
                drmModeFreeConnector(connector);
            }
        }
        return nullptr;
    }
    drmModeModeInfo* find_matching_mode(drmModeConnector* connector, int width, int height, int refresh) {
        for (int i = 0; i < connector->count_modes; i++) {
            drmModeModeInfo* mode = &connector->modes[i];
            if (mode->hdisplay == width && 
                mode->vdisplay == height && 
                abs(static_cast<int>(mode->vrefresh) - refresh) <= 1) {
                return mode;
            }
        }

        for (int i = 0; i < connector->count_modes; i++) {
            drmModeModeInfo* mode = &connector->modes[i];
            if (mode->hdisplay == width && mode->vdisplay == height) {
                return mode;
            }
        }

        return nullptr;
    }
};

PYBIND11_MODULE(DRMUtils, m) {
    py::class_<DRMResolutionManager>(m, "DRMResolutionManager")
        .def(py::init<>())
        .def("openDrm", &DRMResolutionManager::open_drm)
        .def("closeDrm", &DRMResolutionManager::close_drm)
        .def("getCurrentResolution", &DRMResolutionManager::get_current_resolution)
        .def("setResolution", &DRMResolutionManager::set_resolution);
}