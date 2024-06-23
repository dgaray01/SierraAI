const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const dotenv = require('dotenv');
dotenv.config();
const axios = require('axios');
const apiUrl = process.env.API_URL;
const apiToken = process.env.API_TOKEN;
const log = require("../../functions/logger.js")
module.exports = {
	data: new SlashCommandBuilder()
		.setName('ask')
		.setDescription('Ask a question about the university or applications!')
        .addStringOption(option =>
			option
				.setName('question')
				.setDescription('Your question to the bot')
                .setRequired(true)),
                
	async execute(interaction) {
        await interaction.deferReply({ ephemeral: false });
        const reason = interaction.options.getString('question');
        const headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json' 
          };
          
          const data = {
            question: reason
          };
		
		try {
			
			const request = await axios.post(`${apiUrl}/api/ask`, data, { headers });
			console.log(request.data.response)
			const embed = new EmbedBuilder()
  .setAuthor({
    name: "SpiderBot-Ai",
    url: "https://github.com/dgaray01/UR-SpiderBot-AI",
    iconURL: interaction.client.user.avatarURL(),
  })
  .setTitle(reason)
  .setDescription(request.data.response)
  .setColor("#00b0f4")
  .setFooter({
    text: "Powered by SpiderBot-AI",
    iconURL: "https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
  })
  .setTimestamp();

			await interaction.editReply({ embeds: [embed], ephemeral: false });

		} catch (error) {
			console.error('Error fetching API status:', error);
			
            const embed = new EmbedBuilder()
            .setAuthor({
              name: "SpiderBot-Ai",
              url: "https://github.com/dgaray01/UR-SpiderBot-AI",
              iconURL: interaction.client.user.avatarURL(),
            })
            .setTitle("Oops! An error has occurred.")
            .setDescription("Please try again later or contact an administrator.")
            .setColor("#f50000")
            .setFooter({
            text: "Powered by SpiderBot-AI",
              iconURL: "https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
            })
            .setTimestamp();

			await interaction.editReply({ embeds: [embed], ephemeral: false });
            
		}
	},
};
