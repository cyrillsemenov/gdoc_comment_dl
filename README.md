# gdoc_comment_dl
Download all the YouTube links from comments in a GDoc file.

You have to add a path to your Google API credentials .json file is OS variable "GOOGLE_APPLICATION_CREDENTIALS" or as argument --creds when running script.
https://cloud.google.com/docs/authentication/getting-started

### Usage:
- Paste GDoc link or ID
- You can check if links are available (actually not working with Youtube Videos yet)
- Put numbers under in replies comments (easier to navigate as the will be added to filename too)
- Select destination folder (or use autogenerated)
- Wait.

TBD:
- [ ] Check if yt-video available
- [ ] Add other platforms
- [ ] Download pictures
- [x] Make it pretty and stable
- [ ] Make it more pretty and stable