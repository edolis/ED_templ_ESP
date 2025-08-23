#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <driver/gpio.h>
#include <esp_log.h>

#define BLINK_GPIO GPIO_NUM_8

extern "C" void app_main() {
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);
    while (true) {
        gpio_set_level(BLINK_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(500));
        gpio_set_level(BLINK_GPIO, 0);
        vTaskDelay(pdMS_TO_TICKS(500));
        ESP_LOGI("test","ping new 5");
    }
}
