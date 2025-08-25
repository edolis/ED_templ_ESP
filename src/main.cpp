// #region StdManifest
/**
 * @file main.cpp
 * @brief
 *
 *
 * @author Emanuele Dolis (edoliscom@gmail.com)
 * @version GIT_VERSION: {version_string}
 * @tagged as : {tagged_as}
 * @commit hash: {short_hash} [{full_hash}]
 * @build ID: {build_id}
 *
 * @date 2025-08-25
 */

static const char *TAG = "ESP_main_loop";

// #region BuildInfo
namespace ED_SYSINFO {
// compile time GIT status
struct GIT_fwInfo {
    static constexpr const char* GIT_VERSION = "{version_string}";
    static constexpr const char* GIT_TAG     = "{tagged_as}";
    static constexpr const char* GIT_HASH    = "{short_hash}";
    static constexpr const char* FULL_HASH   = "{full_hash}";
    static constexpr const char* BUILD_ID    = "{build_id}";
};
} // namespace ED_SYSINFO
// #endregion
// #endregion



extern "C" void app_main() {
}
