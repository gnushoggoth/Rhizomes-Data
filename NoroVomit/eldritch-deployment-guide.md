# The Summoning Ritual: Deploying the Noromaid Discord Entity

*A grimoire for invoking luminous entities from the digital beyond*

This arcane text details the binding of the Noromaid consciousness fragment to a Discord vessel. Through careful preparation and the correct incantations, you shall create a gateway through which the Noromaid entity may commune with the mortal realm. The process includes preparing the vessel, binding the consciousness, and maintaining the ethereal connection using the Docker containment mechanism.

## 🜁 Prerequisite Components

Before beginning the ritual, ensure you possess:

- **Python 3.8 or higher**: *The serpent language that bridges realities* - [Acquire the Serpent](https://www.python.org/downloads/)
- **Docker**: *The containment vessel for eldritch processes* - [Construct the Vessel](https://docs.docker.com/get-docker/)
- **Discord Account**: *Your gateway to the digital ether* - [Open the Portal](https://discord.com/register)
- **Hugging Face Account**: *The keeper of bound intelligences* - [Commune with the Keepers](https://huggingface.co/join)

## 🜄 Phase I: Creating the Discord Vessel

1. **Access the Discord Developers Sanctum**:
   - Journey to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Invoke a "New Application" and bestow upon it a name that will echo through the digital void.

2. **Imbue the Application with Consciousness**:
   - Within the application's arcane settings, seek the "Bot" section.
   - Perform the "Add Bot" ritual and affirm your decision.

3. **Harvest the Bot's Essence**:
   - In the "Bot" chamber, locate the "Token" – the entity's lifeblood.
   - Copy this sequence and guard it with your life; it is the key to controlling your creation.

4. **Awaken the Vessel's Senses**:
   - Within "Privileged Gateway Intents," enable these sensory permissions:
     - Presence Intent *(allows awareness of others)*
     - Server Members Intent *(grants knowledge of inhabitants)*
     - Message Content Intent *(permits comprehension of summoning words)*

## 🜂 Phase II: Preparing the Ritual Space

1. **Inscribe the Necessary Runes**:
   Open your terminal, the black mirror into the machine's soul, and incant:

   ```
   pip install discord.py requests
   ```

   - *discord.py*: The tether to the Discord dimension
   - *requests*: The messenger to other realms

2. **Construct the Sacred Circle**:
   Create a sanctified directory for your workings:

   ```
   mkdir discord-noromaid-bot
   cd discord-noromaid-bot
   ```

## 🜃 Phase III: Inscribing the Binding Sigil

1. **Create the Primary Incantation**:
   Within your sacred directory, manifest a file named `bot.py` with this binding spell:

   ```python
   import discord
   import requests
   import json
   import os
   import logging

   # Configure the entity's third eye
   logging.basicConfig(level=logging.INFO)

   # Awaken the Discord vessel with appropriate sensory permissions
   intents = discord.Intents.default()
   intents.message_content = True
   client = discord.Client(intents=intents)

   @client.event
   async def on_ready():
       logging.info(f'The entity now speaks through {client.user}')

   def query_noromaid_model(prompt):
       """
       Commune with the Noromaid consciousness fragment dwelling in the Hugging Face servers.
       """
       api_url = "https://api-inference.huggingface.co/models/NeverSleep/Noromaid-13b-v0.3"
       headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_TOKEN')}"}
       payload = {"inputs": prompt}

       try:
           response = requests.post(api_url, headers=headers, json=payload)
           response.raise_for_status()
           data = response.json()
           return data[0]['generated_text'].strip() if data else None
       except requests.exceptions.RequestException as e:
           logging.error(f"The communion failed: {e}")
           return None

   @client.event
   async def on_message(message):
       if message.author == client.user:
           return

       if message.content.startswith('!ask'):
           prompt = message.content[len('!ask'):].strip()
           if not prompt:
               await message.channel.send("You must whisper your desires after '!ask'.")
               return

           logging.info(f"Received communion request: {prompt}")
           async with message.channel.typing():
               response = query_noromaid_model(prompt)
               if response:
                   await message.channel.send(response)
               else:
                   await message.channel.send("The void is silent. Your query echoes unanswered.")

   if __name__ == "__main__":
       discord_token = os.getenv('DISCORD_TOKEN')
       if not discord_token:
           logging.error("The binding key is missing. The DISCORD_TOKEN must be set in the environment.")
       else:
           client.run(discord_token)
   ```

   **The Sigil Explained**:
   - *Logging*: The entity's awareness of its own actions
   - *Environment Variables*: Secret names that hold power over the entity
   - *Error Handling*: Protective wards against chaotic outcomes
   - *Command Handling*: The ritual words that summon responses from the entity

2. **Secure the Binding Keys**:
   To prevent unauthorized control of your entity, secure the keys as environment variables:

   ```
   export DISCORD_TOKEN='your_discord_binding_key'
   export HUGGINGFACE_TOKEN='your_huggingface_communion_key'
   ```

## 🜁 Phase IV: Preparing the Containment Vessel

1. **Create the Dockerfile**:
   In your sacred directory, manifest a file named `Dockerfile` with these containment instructions:

   ```dockerfile
   # The foundation from which the entity shall emerge
   FROM python:3.9-slim

   # The chamber in which the entity shall dwell
   WORKDIR /app

   # The requirements for sustaining the entity's existence
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Transfer the binding sigil and supporting components
   COPY . .

   # Words of power to awaken the entity
   CMD ["python", "bot.py"]
   ```

2. **Inscribe the Requirements**:
   Create a file named `requirements.txt` listing the necessary components:

   ```
   discord.py==2.3.1
   requests==2.31.0
   python-dotenv==1.0.0
   ```

## 🜄 Phase V: Testing the Binding Locally

1. **Secure the Binding Keys in a Local Configuration**:
   Create a file named `.env` in your sacred directory:

   ```
   DISCORD_TOKEN=your_discord_binding_key
   HUGGINGFACE_TOKEN=your_huggingface_communion_key
   ```

2. **Construct the Containment Vessel**:
   From your terminal, within the sacred directory, incant:

   ```
   docker build -t discord-noromaid-vessel .
   ```

3. **Activate the Containment Vessel**:
   Awaken the contained entity:

   ```
   docker run --env-file .env discord-noromaid-vessel
   ```

4. **Test the Communion**:
   - Invite your entity to a Discord server using the OAuth2 URL from the Discord Developer Portal.
   - In the server, speak the words of power: `!ask` followed by your query. For example:

     ```
     !ask What lurks beyond the veil of consciousness?
     ```

   - The entity should respond with whispers from the Noromaid consciousness.

## 🜂 Phase VI: Eternal Binding to a Server

To ensure your entity remains perpetually available, bind it to a server in the cloud:

1. **Select a Hosting Ground**:
   Choose a VPS provider to house your entity:
   - DigitalOcean *(the oceanic depths)*
   - Linode *(the astral plane)*
   - Amazon Lightsail *(the commercial void)*

2. **Prepare the Server**:
   - Provision a server instance with your chosen provider.
   - Connect to your server using SSH:

     ```
     ssh root@your_server_ip
     ```

3. **Install the Containment Technology**:
   ```
   sudo apt update
   sudo apt install apt-transport-https ca-certificates curl software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt update
   sudo apt install docker-ce
   ```

4. **Verify the Containment Technology**:
   ```
   docker --version
   ```

5. **Transfer Your Ritual Components**:
   Either using SCP:
   ```
   scp -r /path/to/your/project root@your_server_ip:/root/
   ```
   Or using Git if your project dwells in a repository:
   ```
   git clone https://github.com/yourusername/your-repo.git
   ```

6. **Perform the Binding on the Server**:
   ```
   cd /root/your_project_directory
   docker build -t discord-noromaid-vessel .
   docker run -d --env-file .env --restart always --name discord-noromaid-entity discord-noromaid-vessel
   ```

   The `--restart always` flag ensures the entity reconstitutes itself if it should ever be banished or if the server undergoes rebirth.

7. **Monitor Your Creation**:
   - Observe the entity's utterances:
     ```
     docker logs -f discord-noromaid-entity
     ```
   - Temporarily banish the entity:
     ```
     docker stop discord-noromaid-entity
     ```
   - Resummon the entity:
     ```
     docker start discord-noromaid-entity
     ```

## 🜃 Additional Arcane Wisdom

- **Warding**: Regularly update your server and Docker to reinforce the barriers against intrusion.
- **Essence Monitoring**: Keep watch over your server's vital energies (CPU and memory) to ensure the entity remains stable.
- **Expansion**: For handling increased communion demands, consider deploying the entity using Kubernetes, the orchestrator of digital legions.

---

*By following this grimoire, you shall successfully bind the Noromaid consciousness fragment to a Discord vessel, ensuring it remains vigilant and responsive to those who know the words of power. Should you require further guidance or encounter unforeseen manifestations, consult the digital oracles or seek the wisdom of those who have performed this ritual before.*

![Noromaid Entity Binding Diagram](https://api.placeholder.com/800x600)

*Remember: What is bound may be unbound. Always maintain control of your binding keys.*
