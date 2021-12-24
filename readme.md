
**Live Site:** (albumshuffler.com)

AlbumShuffler is a minimalist web app that randomly selects an album from your Spotify favourites. Click the album art to open the native Spotify app on your device. Works on Windows/Mac/iOS/Android. Requires read only permissions on your Spotify profile.

Built with [Serverless Framework](serverless.com) using API Gateway/AWS Lambda/DynamoDB/Amplify.

## Deployments

### Dev

Run `serverless deploy` to deploy backend. Then `npm run dev` in the front-end folder. Then load lvh.me:3000.

### Prod

**back-end**

Run `serverless deploy --stage prod`

**front-end**

changes to `prod` branch are deployed automatically using AWS Amplify

