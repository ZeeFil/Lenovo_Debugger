import { pingDevice } from './src/services/cloudRelay';
pingDevice().then(res => {
  console.log("PING RESULT:", res);
  process.exit(0);
}).catch(err => {
  console.error("PING ERROR:", err);
  process.exit(1);
});
