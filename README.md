# UR-SpiderBot-AI


SpiderBot-AI is an advanced artificial intelligence designed for universities to train data on websites to provide easy access to students to answers about applications and information about the institution.

## Features

- **Intelligent Discord Bot**: Includes a Discord Bot easy to use for communities.
- **Local HTTP server**: Includes an HTTP server for requesting data.
- **Customization**: Easily customizable for your institution

## Requirements
SpiderBot-AI needs a Python and a Node.js environment to function properly. 
### Python Environment (Server)

To set up SpiderBot-AI Server, ensure you have Python installed. The project requires additional dependencies and Microsoft C++ Build Tools for some of its libraries.

1. **Install Python**: [Download Python](https://www.python.org/downloads/) and follow the installation instructions for your operating system.
   
2. **Microsoft C++ Build Tools**: Some Python packages may require Microsoft C++ Build Tools. Install them from [Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

3. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/spiderbot-ai.git
   cd spiderbot-ai
   ```

4. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
### Node.js Environment (Bot)

To set up SpiderBot-AI in a Node.js environment, ensure you have Node.js installed.

1. **Install Node.js**: [Download Node.js](https://nodejs.org/en/download/) and follow the installation instructions for your operating system.

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/spiderbot-ai.git
   cd spiderbot-ai
   ```

3. **Install Node.js Dependencies**:
   ```bash
   npm install
   ```
## Configuration

SpiderBot-AI uses a configuration file to manage settings. 

**Rename example.env to .env**
```bash
$ mv ./example.env .env
$ mv ./discord/example.env ./discord/.env
```
Fill both of your .env files with the data requested.

You must obtain the following tokens:
1. [HUGGINGFACEHUB API TOKEN](https://huggingface.co/docs/hub/en/security-tokens)
2. [DISCORD BOT TOKEN](https://discord.dev)



## Usage

### Python

After setting up the Python environment, you can start the HTTP server with the following command:

```bash
python app.py
```

### Node.js

Once the Node.js environment is set up, start the bot application with:

```bash
node app.js
```

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

