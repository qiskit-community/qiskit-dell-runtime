# Hybrid Emulation Platform
Qiskit Runtime Emulator is a [Qiskit Runtime]() platform that can execute classical-quantum code on both local and on-premise environments. With this platform, hybrid classical-quantum code bundle can be developed and executed. Powered by Qiskit Runtime API, this execution model provides close-integration of classical and quantum execution. 

Various simulation, emulation and quantum hardware can be integrated with this platform. Developers can abstract their source code with Qiskit, so that execution can be ported across execution environments with minimum effort. 

## Architecture
This platform provides both server-side provider and 

![Qiskit Runtime Architecture](images/arch.png)
### Client-side Provider
Users would need to install the `qiskit-emulation-provider` on client devices. The provider is defaulted to local execution and can be used out of the box. This provider can also be used to connect with platform running on a server-side, so that users can control server and execute jobs by using the same API. 

### Server-side Components
This platform has a minimalist design to create a light-weighted execution environment for server-side components. It contains an `orchestrator` long-running microservice that listens to requests for `qiskit-emulation-provider`. 

At runtime, when a job is started by user, a new pod will be created to execute both classical and vQPU workload. 

For deployment installation, please visit this [link](doc/install.md). 

### Database Configuration
All user-uploaded code and execution parameters will be stored in a database. By 

### SSO
SSO integration is off by default, so that users can easily set up a sandbox environment. There is integration

### Multi-Backend Support
By default, the quantum execution will be processed by [Qiskit Aer] simulation engine. Users can modify the quantum backend by specifying `backend-name` in the job input parameter. Custom code adjustment can be made to support multiple [qiskit backends](), including other emulation, simulation and QPU backends. 

## Emulation vs Simulation
While simulation engines execute quantum circuits to measure probablistic outcome, emulation engines calculate outcome for algorithms with deterministic calculations. 

**The Hybrid Emulation Platform can support both simulation and emulation,** depending on the backend used. 

Emulations for different use cases are under-development, and we are looking for feedback to better prioritize on use cases. If you have a use-case in mind, please contact us at [v.fong@dell.com](mailto:v.fong@dell.com).

## Documentation Links:
- [Introduction](doc/intro.md)
- [Installation Guide](doc/install.md)
  - [Custom Database Configuration]()
- [Usage]()
- [Examples]()
  - [Local Execution]()
  - [Remote Execution]()
  - [QKA]()
  - [VQE]()
  - [Custom Backend]()


For any questions or feedback, please contact [v.fong@dell.com](mailto:v.fong@dell.com)