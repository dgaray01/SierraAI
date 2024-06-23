function log(level, message) {
    const now = new Date();
    const timestamp = `${now.toISOString().slice(0, 19)} - ${level.toUpperCase()} -`;
    console.log(`${timestamp} ${message}`);
}

module.exports = log;
