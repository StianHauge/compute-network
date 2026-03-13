use bollard::container::{
    Config, CreateContainerOptions, ListContainersOptions, RemoveContainerOptions, StopContainerOptions,
};
use bollard::image::CreateImageOptions;
use bollard::service::HostConfig;
use bollard::Docker;
use futures_util::stream::StreamExt;
use std::collections::HashMap;
use tracing::{error, info};

pub struct DockerOrchestrator {
    docker: Docker,
}

impl DockerOrchestrator {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let docker = Docker::connect_with_local_defaults()?;
        Ok(Self { docker })
    }

    pub async fn pull_image(&self, image_url: &str) -> Result<(), Box<dyn std::error::Error>> {
        info!("Pulling image: {}", image_url);
        
        let mut stream = self.docker.create_image(
            Some(CreateImageOptions {
                from_image: image_url,
                ..Default::default()
            }),
            None,
            None,
        );

        while let Some(msg) = stream.next().await {
            match msg {
                Ok(info) => {
                    if let Some(status) = info.status {
                        info!("Docker Pull: {}", status);
                    }
                }
                Err(e) => {
                    error!("Error pulling image: {}", e);
                    return Err(Box::new(e));
                }
            }
        }
        
        info!("Successfully pulled image: {}", image_url);
        Ok(())
    }

    pub async fn start_agent(&self, image_url: &str, container_name: &str, host_port: u16) -> Result<(), Box<dyn std::error::Error>> {
        info!("Starting new Agent container: {} on port {}", container_name, host_port);

        // Ensure IPC directory exists for UNIX sockets
        let _ = std::fs::create_dir_all("/tmp/averra_ipc");

        let mut port_bindings = HashMap::new();
        port_bindings.insert(
            "8000/tcp".to_string(),
            Some(vec![bollard::service::PortBinding {
                host_ip: Some("0.0.0.0".to_string()),
                host_port: Some(host_port.to_string()),
            }]),
        );

        let host_config = HostConfig {
            port_bindings: Some(port_bindings),
            binds: Some(vec!["/tmp/averra_ipc:/tmp/averra_ipc".to_string()]),
            // In a real environment we would inject Device requests for GPU passthrough
            // Setting up barebones first
            ..Default::default()
        };

        let config = Config {
            image: Some(image_url),
            host_config: Some(host_config),
            env: Some(vec!["NODE_TYPE=community", "NODE_LOCATION=GCP"]),
            ..Default::default()
        };

        let options = Some(CreateContainerOptions {
            name: container_name,
            platform: None,
        });

        let id = self.docker.create_container(options, config).await?.id;
        self.docker.start_container::<String>(&id, None).await?;
        
        info!("Container {} started successfully.", container_name);
        Ok(())
    }

    pub async fn stop_agent(&self, container_name: &str) -> Result<(), Box<dyn std::error::Error>> {
        info!("Stopping old Agent container: {}", container_name);
        
        match self.docker.stop_container(container_name, None).await {
            Ok(_) => info!("Stopped {}", container_name),
            Err(bollard::errors::Error::DockerResponseServerError { status_code: 304, .. }) => {
                info!("Container {} was already stopped.", container_name);
            }
            Err(bollard::errors::Error::DockerResponseServerError { status_code: 404, .. }) => {
                info!("Container {} does not exist.", container_name);
                return Ok(());
            }
            Err(e) => return Err(Box::new(e)),
        }
        
        let remove_opts = Some(RemoveContainerOptions {
            force: true,
            ..Default::default()
        });
        
        self.docker.remove_container(container_name, remove_opts).await?;
        info!("Removed {}", container_name);
        Ok(())
    }
}
