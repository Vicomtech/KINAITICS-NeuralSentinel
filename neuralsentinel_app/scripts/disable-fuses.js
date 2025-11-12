// Required dependencies for working with Electron fuses
const path = require('path');
const { flipFuses, FuseVersion, FuseV1Options } = require('@electron/fuses');

module.exports = async function(context) {
  // First, we define the name of the executable that will be generated.
  // The 'exeName' will use the product filename, adding ".exe" at the end.
  const exeName = `${context.packager.appInfo.productFilename}.exe`;
  const exePath = path.join(context.appOutDir, exeName);

  console.log(`🔧 [afterPack] flipping fuses in ${exePath}`);

  // Next, we adjust the fuses in the executable.
  // We flip the fuses based on the configuration options needed for our app.
  await flipFuses(
    exePath,
    {
      version: FuseVersion.V1, // We are using the first version of fuses
      [FuseV1Options.RunAsNode]: false,  // Disable running as a Node.js process
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false, // Disable Node.js options environment variable
      [FuseV1Options.EnableNodeCliInspectArguments]: false, // Disable CLI inspect arguments
      [FuseV1Options.EnableCookieEncryption]: true, // Enable cookie encryption
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true, // Enable ASAR integrity validation
      [FuseV1Options.OnlyLoadAppFromAsar]: true, // Restrict the app to load only from ASAR
    }
  );

  // Once the fuses are adjusted, we confirm that the operation was successful
  console.log('Fuses adjusted successfully');
};