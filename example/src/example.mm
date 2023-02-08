#include <bootloader.hpp>

// Hook function defined in patcher/main.py
void $CCScheduler_update(void* schedulerObject, float deltaTime) {
	CCScheduler_update(schedulerObject, deltaTime / 2);
}
