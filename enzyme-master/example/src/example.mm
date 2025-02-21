#include <bootloader.hpp>
#include "breakpoint_hooks.h"


void $CCScheduler_update(void* schedulerObject, float deltaTime) {
    static void* original = nullptr;
    if (!original) {
        CCScheduler_update(schedulerObject, deltaTime / 2);
        return;
    }
    ((void(*)(void*, float))original)(schedulerObject, deltaTime / 2);
}
