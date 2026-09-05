use hmac::{Hmac, Mac};
use sha2::Sha256;
use chrono::Utc;

type HmacSha256 = Hmac<Sha256>;

pub struct GmoExecutionClient {
    api_key: String,
    secret_key: String,
}

impl GmoExecutionClient {
    pub fn new(api_key: String, secret_key: String) -> Self {
        Self { api_key, secret_key }
    }

    pub fn generate_headers(&self, method: &str, path: &str, body: &str) -> Result<(String, String, String), String> {
        let timestamp = Utc::now().timestamp_millis().to_string();
        let text = format!("{}{}{}{}", timestamp, method, path, body);
        
        let mut mac = HmacSha256::new_from_slice(self.secret_key.as_bytes())
            .map_err(|e| e.to_string())?;
        mac.update(text.as_bytes());
        let sign = hex::encode(mac.finalize().into_bytes());

        Ok((self.api_key.clone(), timestamp, sign))
    }
}
