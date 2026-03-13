use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use tracing::{error, info, warn};

#[derive(Serialize, Deserialize, Debug)]
pub struct UpdateCommand {
    pub command: String,
    pub target_version: String,
    pub image_url: String,
}

pub struct CommandListener {
    url: String,
}

impl CommandListener {
    pub fn new(node_id: &str) -> Self {
        let url = format!("ws://127.0.0.1:8000/ws/sentinel/{}", node_id);
        Self { url }
    }

    // This method takes a callback function that handles the update instruction
    pub async fn listen<F>(&self, mut on_update: F) 
    where
        F: FnMut(UpdateCommand) -> futures_util::future::BoxFuture<'static, Result<(), Box<dyn std::error::Error>>>,
    {
        loop {
            info!("Attempting to connect to Control Plane (Sentinel Stream): {}", self.url);
            
            match connect_async(&self.url).await {
                Ok((mut ws_stream, _)) => {
                    info!("Sentinel connected to Control Plane.");
                    
                    while let Some(msg) = ws_stream.next().await {
                        match msg {
                            Ok(Message::Text(text)) => {
                                match serde_json::from_str::<UpdateCommand>(&text) {
                                    Ok(cmd) => {
                                        if cmd.command == "UPDATE_AVAILABLE" {
                                            info!("Received UPDATE_AVAILABLE signal for version: {}", cmd.target_version);
                                            if let Err(e) = on_update(cmd).await {
                                                error!("Failed to process update: {}", e);
                                            }
                                        }
                                    }
                                    Err(e) => warn!("Received invalid payload: {}", e),
                                }
                            }
                            Ok(Message::Close(_)) => {
                                warn!("Connection closed by Control Plane.");
                                break;
                            }
                            Err(e) => {
                                error!("WebSocket error: {}", e);
                                break;
                            }
                            _ => {}
                        }
                    }
                }
                Err(e) => {
                    error!("WebSocket connection failed: {}. Retrying in 5s...", e);
                }
            }
            
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
        }
    }
}
