mod docker;
mod network;

use crate::docker::DockerOrchestrator;
use crate::network::{CommandListener, UpdateCommand};
use std::sync::Arc;
use tracing::{info, error};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();
    
    info!("Starting Averra Sentinel...");
    
    // In a real app we'd fetch the Node ID from config or arguments
    let node_id = std::env::var("NODE_ID").unwrap_or_else(|_| "mock-node-123".to_string());
    
    let orchestrator = Arc::new(DockerOrchestrator::new()?);
    let listener = CommandListener::new(&node_id);
    
    // State tracking for Blue-Green
    // E.g., Active port: 8081 or 8082
    let mut current_version = "1.1".to_string();
    let mut current_container = "averra-agent-green".to_string();
    let mut current_port = 8081;
    
    listener.listen(|cmd: UpdateCommand| {
        let orchestrator = orchestrator.clone();
        
        let target_ver = cmd.target_version.clone();
        let target_img = cmd.image_url.clone();
        
        let old_container = current_container.clone();
        
        // Toggle green/blue based on current
        let new_container = if current_container == "averra-agent-green" {
            "averra-agent-blue".to_string()
        } else {
            "averra-agent-green".to_string()
        };
        
        let new_port = if current_port == 8081 { 8082 } else { 8081 };
        
        let old_version = current_version.clone();
        
        current_version = target_ver.clone();
        current_container = new_container.clone();
        current_port = new_port;
        
        Box::pin(async move {
            info!("--- STARTING BLUE-GREEN DEPLOYMENT (v{} -> v{}) ---", old_version, target_ver);
            
            // 1. Pull the new image in background
            orchestrator.pull_image(&target_img).await?;
            
            // 2. Start the new container on the alternate port
            orchestrator.start_agent(&target_img, &new_container, new_port).await?;
            
            info!("Waiting for new agent to initialize...");
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
            
            // 3. Graceful decay: Stop and remove the old container
            // In a real scenario we'd wait for Control Plane to confirm the new one via HTTP ping
            info!("Decoherence: Killing old agent container {}", old_container);
            let _ = orchestrator.stop_agent(&old_container).await;
            
            info!("--- DEPLOYMENT COMPLETE ---");
            Ok(())
        })
    }).await;
    
    Ok(())
}
