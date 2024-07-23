const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const dotenv = require('dotenv');
dotenv.config();
const axios = require('axios');
const apiUrl = process.env.API_URL;
const apiToken = process.env.API_TOKEN;
const log = require("../../functions/logger.js")
module.exports = {
	data: new SlashCommandBuilder()
		.setName('status')
		.setDescription('Check the current state of the bot and API'),
	async execute(interaction) {
		const headers = {
			'Authorization': `Bearer ${apiToken}`
		};
		
		try {
			
			const response = await axios.get(`${apiUrl}/api/status`, { headers });
			let API_status = '❌ Down';
			if (response.data.status === "Ok") {
				API_status = '✅ Up';
			}
			
			const embed = new EmbedBuilder()
				.setAuthor({
					name: interaction.client.user.username,
					url: "https://github.com/dgaray01/SierraAI",
					iconURL: interaction.client.user.avatarURL(),
				})
				.setTitle("Service Status")
				.setDescription("Check the status of our service and API!")
				.addFields(
					{name: "Discord's API", value: `${interaction.client.ws.ping.toString()}ms`, inline: true},
					{name: "Server API", value: API_status, inline: true},
					{name: "Server", value: API_status, inline: true},
				)
				.setThumbnail(interaction.client.user.avatarURL())
				.setColor("#00b0f4");
			
			await interaction.reply({ embeds: [embed], ephemeral: true });

		} catch (error) {
			console.error('Error fetching API status:', error);
			
			const embed = new EmbedBuilder()
				.setAuthor({
					name: interaction.client.user.username,
					url: "https://github.com/dgaray01/SierraAI",
					iconURL: interaction.client.user.avatarURL(),
				})
				.setTitle("Service Status")
				.setDescription("Check the status of our service and API!")
				.addFields(
					{name: "Discord's API", value: `${interaction.client.ws.ping.toString()}ms`, inline: true},
					{name: "Server API", value: '❌ Down', inline: true}, // Assuming server API is down
					{name: "Server", value: '❌ Down', inline: true}, // Assuming server itself is down
				)
				.setThumbnail(interaction.client.user.avatarURL())
				.setColor("#ff0000");

			await interaction.reply({ embeds: [embed], ephemeral: true });
		}
	},
};
