# Tasker Design

Tasker plays a crucial role in the "Decentralist Mobile Assistant" system as it acts as the bridge between the user's phone and the intelligent agents running on the computer. Tasker is an automation app for Android that allows users to create custom tasks and automate various actions on their devices. In this section, we will explore the design of Tasker and how it integrates with the rest of the system.

## Tasker as an HTTP Server
To enable communication between the CrewAI agents on the computer and the user's phone, Tasker will be configured as an HTTP server. Here's how it will work:

1. HTTP Server Configuration:
   - Tasker will be set up to listen for incoming HTTP requests on a specific port.
   - The HTTP server will be configured to accept POST requests, as the CrewAI agents will send data using the POST method.
   - Tasker will be configured to parse the incoming JSON payloads and extract relevant information.

2. Request Handling:
   - When Tasker receives an HTTP request from a CrewAI agent, it will first validate the request to ensure it adheres to the expected format and contains the necessary data.
   - Tasker will parse the JSON payload and extract the following information:
     - `type`: Indicates the type of content being sent (e.g., "text" for plain text, "file" for a file path).
     - `content`: The actual content or file path being transmitted.
     - `app` (optional): Specifies the target application on the phone to handle the content (e.g., "VLC" for playing videos).
   - Based on the extracted information, Tasker will trigger the appropriate action or task on the user's phone.

## Tasker Actions and Tasks
Tasker will be designed to perform specific actions and tasks based on the received requests from CrewAI agents. The two main tasks identified are:

1. Read Text:
   - When Tasker receives a request with the `type` set to "text", it will invoke the "Read Text" task.
   - The "Read Text" task will use the ElevenLabs Text-to-Speech (TTS) engine to convert the received text into speech.
   - Tasker will play the generated speech audio on the user's phone, providing a hands-free and convenient way to consume the information.

2. Open File:
   - When Tasker receives a request with the `type` set to "file", it will trigger the "Open File" task.
   - The "Open File" task will use the file path provided in the `content` field to locate the file on the user's phone.
   - If the `app` field is specified in the request, Tasker will use that application to open the file. For example, if the `app` is set to "VLC", Tasker will open the file using the VLC media player.
   - If no specific application is provided, Tasker will use the default application associated with the file type to open it.

## Integration with ElevenLabs TTS
To enable high-quality text-to-speech functionality, Tasker will integrate with the ElevenLabs TTS engine. Here's how the integration will work:

1. ElevenLabs API:
   - Tasker will use the ElevenLabs API to convert text to speech.
   - The API will be configured with the necessary credentials and endpoints to access the ElevenLabs TTS service.

2. Text-to-Speech Conversion:
   - When the "Read Text" task is triggered, Tasker will send the text received from the CrewAI agent to the ElevenLabs API.
   - The ElevenLabs API will process the text and generate an audio file containing the speech output.
   - Tasker will retrieve the generated audio file from the API response.

3. Audio Playback:
   - Once the audio file is obtained, Tasker will use the built-in media playback capabilities of Android to play the speech audio on the user's phone.
   - The audio will be played through the phone's speakers or any connected audio output devices, such as headphones or Bluetooth speakers.

## Error Handling and Notifications
To ensure a smooth user experience and provide informative feedback, Tasker will implement error handling and notification mechanisms:

1. Error Handling:
   - If Tasker encounters an error while processing a request or performing a task, it will capture and log the error details.
   - Tasker will send an error response back to the CrewAI agent, indicating the nature of the error and any relevant error codes.
   - The error details will be stored in Tasker's logs for further analysis and debugging purposes.

2. Notifications:
   - Tasker will display notifications on the user's phone to keep them informed about important events or status updates.
   - Notifications will be triggered in various scenarios, such as:
     - When a new request is received from a CrewAI agent.
     - When a task (e.g., "Read Text" or "Open File") is successfully completed.
     - When an error occurs during task execution.
   - The notifications will provide brief and informative messages to the user, along with any necessary actions they can take (e.g., retrying a failed task).

## Configuration and Customization
Tasker will offer configuration options and customization settings to tailor the behavior of the "Decentralist Mobile Assistant" system on the user's phone:

1. HTTP Server Settings:
   - Users will be able to configure the port number on which Tasker listens for incoming HTTP requests.
   - Advanced users may have the option to customize the HTTP server's behavior, such as setting authentication requirements or enabling HTTPS for secure communication.

2. TTS Settings:
   - Tasker will provide settings to adjust the text-to-speech output, such as selecting the preferred ElevenLabs voice, adjusting the speech rate, or setting the default volume.
   - Users will have the flexibility to configure different TTS settings for various scenarios or contexts.

3. Notification Preferences:
   - Users will have control over the notification behavior of Tasker.
   - They will be able to enable or disable specific types of notifications, set notification priorities, or customize the notification sounds and vibration patterns.

4. Task Customization:
   - Advanced users may have the ability to modify or extend the default tasks in Tasker, such as "Read Text" or "Open File".
   - Tasker will provide a user-friendly interface for creating custom tasks or editing existing ones, allowing users to define their own automation workflows.

*Analogy: Tasker can be compared to a personal assistant on the user's phone. Just like a personal assistant, Tasker is always ready to receive requests, perform tasks, and provide feedback to the user. It acts as the user's reliable companion, executing actions based on the instructions received from the CrewAI agents, much like how a personal assistant follows the directives given by their employer.*

By designing Tasker as an HTTP server and integrating it with the ElevenLabs TTS engine, the "Decentralist Mobile Assistant" system enables seamless communication between the user's phone and the intelligent agents running on the computer. Tasker's ability to perform tasks like reading text aloud and opening files on the user's phone enhances the system's functionality and provides a convenient and hands-free experience for the user.

As the system evolves, Tasker's design can be further expanded to include additional tasks, integrations with other mobile apps or services, and more advanced automation capabilities. Regular updates and improvements to Tasker will ensure it remains a reliable and efficient component of the "Decentralist Mobile Assistant" system.

Remember, the success of Tasker's design lies in its ability to bridge the gap between the user's phone and the computer-based agents, providing a seamless and intuitive experience for the user. By carefully crafting Tasker's functionality, error handling, and customization options, the "Decentralist Mobile Assistant" system can deliver a truly powerful and personalized mobile experience.