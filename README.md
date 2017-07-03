# Home-Power-Monitor
My first hobby project in Python, apologies for the mess.
You require an Envoy S home power meter to use this.
It is best to run on a Raspberry Pi or similar, as it's current state basically steals the system display every minute to display the plot. If I had time away from other projects I'd figure out a way to save the image or use matplotlibs animate function.

If you do want to use this, feel free, you just need to change your $envoy ip address on line 11 to whatever yours is. Suggest making it a static IP in your router config.
