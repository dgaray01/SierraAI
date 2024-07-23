const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const {ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const webhookURL = 'https://discord.com/api/webhooks/1264719519637704776/Fzy-VhRFV2KXWoPHaED9kpI4zLDk-2CF-M3BYuRRHRA95qJjImRSqXLm1sp-SQU3MrML';

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
        await interaction.deferReply({ ephemeral: true });
        const reason = interaction.options.getString('question');
        if (256 <= reason.length) return await interaction.followUp({ content: '❌ | Oops! Your prompt must be below 256 characters.', ephemeral: true });
        const headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json' 
          };
          
          const data = {
            question: reason
          };
		
		try {
			
			const request = await axios.post(`${apiUrl}/api/ask`, data, { headers });

      function splitMessage(message, size) {
        const chunks = [];
        let start = 0;
        while (start < message.length) {
          chunks.push(message.slice(start, start + size));
          start += size;
        }
        return chunks;
      }
      

      const content = request.data.response;
      

      const MAX_EMBED_DESCRIPTION_LENGTH = 4096;
      const chunks = content.length > MAX_EMBED_DESCRIPTION_LENGTH ? splitMessage(content, MAX_EMBED_DESCRIPTION_LENGTH) : [content];
      
      // Function to create an embed for a specific chunk
      function createEmbed(chunk, reason) {
        return new EmbedBuilder()
          .setAuthor({
            name: interaction.client.user.username,
            url: "https://github.com/dgaray01/SierraAI",
            iconURL: interaction.client.user.avatarURL(),
          })
          .setTitle(reason)
          .setDescription(chunk)
          .setColor("#00b0f4")
          .setFooter({
            text: "Powered by SierraAI",
            iconURL: "https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
          })
          .setTimestamp();
      }
      

      let pageIndex = 0;
      let embed = createEmbed(chunks[pageIndex], reason);
      

      function createNavigationButtons(pageIndex, totalPages) {
        return new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setCustomId('previousPage')
            .setLabel('Previous')
            .setStyle(ButtonStyle.Primary)
            .setDisabled(pageIndex === 0),
          new ButtonBuilder()
            .setCustomId('nextPage')
            .setLabel('Next')
            .setStyle(ButtonStyle.Primary)
            .setDisabled(pageIndex === totalPages - 1)
        );
      }
      
      const linkButton = new ButtonBuilder()
      .setLabel('Learn more about our project')
      .setStyle(ButtonStyle.Link)
      .setURL('https://github.com/dgaray01/SierraAI'); // Replace with your URL

  const row = new ActionRowBuilder()
      .addComponents(linkButton);

      let message = await interaction.editReply({
        embeds: [embed],
        components: chunks.length > 1 ? [createNavigationButtons(pageIndex, chunks.length)] : [row],
        ephemeral: true,
      });
      

      const collector = message.createMessageComponentCollector({ time: 120000 });
      
      collector.on('collect', async i => {
        if (i.customId === 'previousPage') {
          pageIndex--;
        } else if (i.customId === 'nextPage') {
          pageIndex++;
        }
      
        embed = createEmbed(chunks[pageIndex], reason);
      
        await i.update({
          embeds: [embed],
          components: [createNavigationButtons(pageIndex, chunks.length)],
        });
      });
      
      collector.on('end', collected => {
        message.edit({ components: [] });
      });

		} catch (error) {
      console.error('Error fetching API status:', error);

      const embed = new EmbedBuilder()
        .setAuthor({
          name: interaction.client.user.username,
          url: "https://github.com/dgaray01/SierraAI",
          iconURL: interaction.client.user.avatarURL(),
        })
        .setTitle("Oops! An error has occurred.")
        .setDescription("Please try again later or contact an administrator.")
        .setColor("#f50000")
        .setFooter({
          text: "Powered by SierraAI",
          iconURL: "https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
        })
        .setTimestamp();
    
      const button = new ButtonBuilder()
        .setCustomId('reportError')
        .setLabel('Report Error')
        .setStyle(ButtonStyle.Danger);
    
      const row = new ActionRowBuilder()
        .addComponents(button);
    
      await interaction.editReply({ embeds: [embed], components: [row], ephemeral: true });
    
      const filter = i => i.customId === 'reportError' && i.user.id === interaction.user.id;
      const collector = interaction.channel.createMessageComponentCollector({ filter, time: 60000 });
    
      collector.on('collect', async i => {
        if (i.customId === 'reportError') {
          await i.deferUpdate();
    
          try {
            const embed2 = {
              title: "Error Report",
              description: "An error occurred in the application.",
              color: 0xff0000,  // Red color
              fields: [
                  {
                      name: "Error Message",
                      value: error.message || "No message available",
                  },
                  {
                      name: "Stack Trace",
                      value: `\`\`\`${error.stack || "No stack trace available"}\`\`\``,
                  },
                  {
                      name: "Reported By",
                      value: interaction.user.tag || "Unknown user",
                  },
              ],
              timestamp: new Date(),
          };

          const payload = {
            username: 'Error Reporter',
            embeds: [embed2],
        };

        axios.post(webhookURL, payload)
        .then(async response => {
            console.log('Successfully sent error report');
            await i.followUp({ content: 'Error reported successfully. Thank you for helping improve our service!', ephemeral: true });
        })
        .catch(async err => {
            console.error('Error sending error report:', err);
            await i.followUp({ content: 'Failed to report the error. Please try again later.', ephemeral: true });
        });

          } catch (webhookError) {
            console.error('Error sending webhook:', webhookError);
          }
        }
      });
    
      collector.on('end', collected => {
        if (collected.size === 0) {
          interaction.editReply({ components: [] });
        }
      });
    }
    
    // Example usage within your try-catch block
    try {
      // Your code that may throw an error
    } catch (error) {
      await handleError(interaction, error);
    }
	},
};
