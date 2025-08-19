#[cfg(target_os = "android")]
use jni::objects::{JClass, JObject, JString, JValue};
#[cfg(target_os = "android")]
use jni::{JNIEnv, JavaVM};
#[cfg(target_os = "android")]
use jni::sys::{jint, jobject};

#[cfg(target_os = "android")]
use crate::{ScanResult, WiFiNetwork};

#[cfg(target_os = "android")]
static mut JAVA_VM: Option<JavaVM> = None;

#[cfg(target_os = "android")]
#[no_mangle]
pub extern "system" fn JNI_OnLoad(vm: JavaVM, _reserved: *mut std::os::raw::c_void) -> jint {
    android_logger::init_once(android_logger::Config::default().with_min_level(log::Level::Debug));
    
    unsafe {
        JAVA_VM = Some(vm);
    }
    
    jni::sys::JNI_VERSION_1_6
}

#[cfg(target_os = "android")]
fn scan_wifi_android() -> Result<Vec<WiFiNetwork>, String> {
    unsafe {
        if let Some(ref vm) = JAVA_VM {
            let env = vm.get_env().map_err(|e| format!("Failed to get JNI env: {:?}", e))?;
            
            // Get the WiFiScanner class
            let wifi_scanner_class = env.find_class("com/defiwifi/WiFiScanner")
                .map_err(|e| format!("Failed to find WiFiScanner class: {:?}", e))?;
            
            // Get the static scanWiFi method
            let scan_method = env.get_static_method_id(
                wifi_scanner_class,
                "scanWiFi",
                "(Landroid/content/Context;)Ljava/lang/String;"
            ).map_err(|e| format!("Failed to get scanWiFi method: {:?}", e))?;
            
            // Call the method (you'll need to pass a Context - this is simplified)
            let result = env.call_static_method_unchecked(
                wifi_scanner_class,
                scan_method,
                jni::signature::JavaType::Object("java/lang/String".to_string()),
                &[]
            ).map_err(|e| format!("Failed to call scanWiFi: {:?}", e))?;
            
            if let JValue::Object(obj) = result {
                if obj.is_null() {
                    return Err("WiFi scan returned null".to_string());
                }
                
                let java_string: JString = obj.into();
                let rust_string: String = env.get_string(java_string)
                    .map_err(|e| format!("Failed to convert Java string: {:?}", e))?
                    .into();
                
                // Parse JSON result from Java
                let networks: Vec<WiFiNetwork> = serde_json::from_str(&rust_string)
                    .map_err(|e| format!("Failed to parse WiFi networks: {:?}", e))?;
                
                Ok(networks)
            } else {
                Err("Unexpected return type from scanWiFi".to_string())
            }
        } else {
            Err("JavaVM not available".to_string())
        }
    }
}