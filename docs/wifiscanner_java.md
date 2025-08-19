# WiFiScanner Java Class Documentation

This document provides an overview and usage instructions for the `WiFiScanner.java` class, which is part of the Android component of the DefiWifi Flutter application. This class is designed to perform Wi-Fi network scans on Android devices and return the results in a JSON format, which can then be consumed by the Rust backend via JNI.

## Purpose

The `WiFiScanner` class encapsulates the Android-specific logic for scanning available Wi-Fi networks. It leverages Android's `WifiManager` to initiate a scan and a `BroadcastReceiver` to asynchronously capture the scan results. To facilitate synchronous calls from the Rust backend, the `scanWiFi` method employs a `CountDownLatch` to wait for the scan results to become available before returning.

## Location

The `WiFiScanner.java` file is located at:
`android/app/src/main/java/com/defiwifi/WiFiScanner.java`

## Usage

The primary method to interact with this class is the static `scanWiFi` method.

### `scanWiFi(Context context)`

```java
public static String scanWiFi(Context context)
```

-   **Parameters:**
    -   `context`: An Android `Context` object, typically obtained from an `Activity` or `Service`. This is required to access system services like `WifiManager` and to register the `BroadcastReceiver`.

-   **Returns:**
    A `String` containing a JSON array of Wi-Fi network objects. Each object in the array represents a scanned Wi-Fi network and includes the following fields:
    -   `ssid` (String): The service set identifier (SSID) of the network.
    -   `mac` (String): The BSSID (MAC address) of the access point.
    -   `channel` (String): The frequency of the network in MHz.
    -   `signal_level` (int): The detected signal level in dBm.
    -   `timestamp` (long): The timestamp of the scan result in microseconds since boot.
    -   `security` (String): The capabilities of the network, indicating security protocols (e.g., "[WPA2-PSK-CCMP][ESS]").

    In case of an error (e.g., `WifiManager` not available, scan failed to start, or timeout), the returned JSON array will contain a single JSON object with an `"error"` field describing the issue.

-   **Behavior:**
    1.  Initiates a Wi-Fi scan using `WifiManager.startScan()`.
    2.  Registers a `BroadcastReceiver` to listen for `WifiManager.SCAN_RESULTS_AVAILABLE_ACTION`.
    3.  Blocks execution (up to a `SCAN_TIMEOUT_SECONDS` of 10 seconds) using a `CountDownLatch` until scan results are available or the timeout occurs.
    4.  Upon receiving results or timeout, unregisters the receiver and processes the scan results into a JSON array.
    5.  Returns the JSON string.

### Example (from Rust Backend via JNI)

The Rust backend calls this method via JNI. An example of how the Rust code (in `androidsniffer.rs`) might invoke this is:

```rust
// In androidsniffer.rs
let wifi_scanner_class = env.find_class("com/defiwifi/WiFiScanner")
    .map_err(|e| format!("Failed to find WiFiScanner class: {:?}", e))?;

let scan_method = env.get_static_method_id(
    wifi_scanner_class,
    "scanWiFi",
    "(Landroid/content/Context;)Ljava/lang/String;"
).map_err(|e| format!("Failed to get scanWiFi method: {:?}", e))?;

// Assuming 'context_obj' is a JObject representing the Android Context
let result = env.call_static_method_unchecked(
    wifi_scanner_class,
    scan_method,
    jni::signature::JavaType::Object("java/lang/String".to_string()),
    &[JValue::Object(context_obj)]
).map_err(|e| format!("Failed to call scanWiFi: {:?}", e))?;

// Process the 'result' JValue (which will be a JString containing the JSON)
```

## Android Permissions

For the `WiFiScanner` to function correctly, the following permissions **must** be declared in your `android/app/src/main/AndroidManifest.xml` file:

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
```

Additionally, for Android 6.0 (API level 23) and higher, `ACCESS_FINE_LOCATION` or `ACCESS_COARSE_LOCATION` are considered dangerous permissions and require **runtime permission requests** from the user. Your Flutter application (or the native Android code if you're handling it there) must prompt the user to grant these permissions at runtime if they haven't already.

## Error Handling

The `scanWiFi` method includes basic error handling. If the `WifiManager` is not available, the scan fails to start, or a timeout occurs, an error message will be included in the returned JSON array. Individual `JSONException` errors during the processing of scan results are also caught and logged, and an error message is added to the JSON array.

## Considerations

-   **Synchronous Blocking:** The `scanWiFi` method blocks the calling thread (the Rust thread in this case) while waiting for scan results. While this simplifies the JNI interface, it's crucial to ensure that the Rust code calls this method from a background thread to avoid blocking the main application thread and causing ANRs (Application Not Responding).
-   **Timeout:** A `SCAN_TIMEOUT_SECONDS` constant (currently 10 seconds) is used to prevent indefinite blocking. If no scan results are received within this period, the method will return with an error message.
-   **Context:** Ensure that a valid `Context` object is passed to the `scanWiFi` method. An `ApplicationContext` is generally preferred for long-lived operations if an `Activity` context is not strictly necessary, to avoid potential memory leaks.
