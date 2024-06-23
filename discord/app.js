
const fs = require('node:fs');
const path = require('node:path');
const { Client, Collection, Events, GatewayIntentBits } = require('discord.js');
const dotenv = require('dotenv');
const log = require("./functions/logger")
dotenv.config();

const client = new Client({ intents: [GatewayIntentBits.Guilds] });
client.commands = new Collection();

const foldersPath = path.join(__dirname, 'commands');
const commandFolders = fs.readdirSync(foldersPath);


log('debug', 'Starting Application...')

for (const folder of commandFolders) {
	const commandsPath = path.join(foldersPath, folder);
    log('debug', `Loading slash commands in ${commandsPath}...`);
	const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
	for (const file of commandFiles) {
		const filePath = path.join(commandsPath, file);
		const command = require(filePath);
        log('debug', `Slash command ${file} has loaded`);
		if ('data' in command && 'execute' in command) {
			client.commands.set(command.data.name, command);
		} else {
            log('debug', `[WARNING] The command ${filePath} is missing "data" or "execute" property.`)
		}
	}
}

client.on(Events.InteractionCreate, async interaction => {
	if (!interaction.isChatInputCommand()) return;

	const command = interaction.client.commands.get(interaction.commandName);

	if (!command) {
        log('warning', `Command ${interaction.commandName} is given but was not found.`)
		return;
	}

	try {
        log('debug', `Command ${interaction.commandName} has been executed by user ${interaction.user.id}`)
		await command.execute(interaction);
	} catch (error) {
		console.error(error);
        log('error', error)
		if (interaction.replied || interaction.deferred) {
			await interaction.followUp({ content: 'There was an error while executing this command!', ephemeral: true });
		} else {
			await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
		}
	}
});

client.once(Events.ClientReady, readyClient => {
    log('info', `Logged in as ${readyClient.user.tag}`);
});


client.login(process.env.DISCORD_TOKEN);