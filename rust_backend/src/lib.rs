pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}


#[unsafe(no_mangle)]
pub extern "C" fn rust_hello() -> *const std::os::raw::c_char {
    let msg = std::ffi::CString::new("Hello from Rust!").unwrap();
    msg.into_raw() // ⚠️ remember to manage memory!
}