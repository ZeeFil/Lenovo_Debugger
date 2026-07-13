import { doc, onSnapshot, setDoc, getFirestore } from 'firebase/firestore';
import { db } from '../firebase';

export type CommandStatus = 'PENDING' | 'COMPLETED' | 'ERROR';

export interface CommandPayload {
  command: string;
  status: CommandStatus;
  timestamp: number;
  output: string;
}

/**
 * Sends a command via Cloud Relay and waits for a response.
 * @param command The bash command to execute on the tablet.
 * @param timeoutMs How long to wait before giving up (default 10s).
 * @returns The output of the command.
 */
export const executeCloudCommand = async (command: string, timeoutMs: number = 10000): Promise<string> => {
  return new Promise(async (resolve, reject) => {
    try {
      const targetRef = doc(db, 'device_sync', 'target');
      
      await setDoc(targetRef, {
        command,
        status: "PENDING",
        timestamp: Date.now(),
        output: ""
      });

      const unsubscribe = onSnapshot(targetRef, (snapshot) => {
        const data = snapshot.data() as CommandPayload;
        if (data && data.status === 'COMPLETED' && data.command === command) {
          unsubscribe();
          clearTimeout(timer);
          resolve(data.output || "");
        }
      });

      const timer = setTimeout(() => {
        unsubscribe();
        reject(new Error("Timeout reading config via Cloud Relay. Is the tablet_agent.py running?"));
      }, timeoutMs);

    } catch (err) {
      reject(err);
    }
  });
};

/**
 * Reads the Sway configuration file from the tablet.
 */
export const fetchSwayConfig = async (): Promise<string> => {
  return executeCloudCommand("cat ~/.config/sway/config");
};

/**
 * Writes the Sway configuration file to the tablet and reloads Sway.
 */
export const applySwayConfig = async (config: string): Promise<string> => {
  // Use a heredoc to safely write the config
  const cmd = `cat << 'EOF' > ~/.config/sway/config\n${config}\nEOF\nswaymsg reload`;
  return executeCloudCommand(cmd);
};

/**
 * Pings the device to check if the agent is actively listening.
 */
export const pingDevice = async (): Promise<{success: boolean, debug: string}> => {
  try {
    const result = await executeCloudCommand("echo 'pong'", 15000); // 15 second timeout
    const success = result.trim() === 'pong';
    return { success, debug: `Result: '${result}'` };
  } catch (err: any) {
    console.error("Ping failed:", err);
    return { success: false, debug: `Error: ${err.message}` };
  }
};
