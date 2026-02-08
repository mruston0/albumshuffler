class AlbumShufflerApi {

    constructor() {
        this.prefetchedAlbum = null;
        this._prefetchPromise = null;
    }

    prefetchNextAlbum() {
        this._prefetchPromise = this.get_spotify_random_album()
            .then(response => response.json())
            .then(data => {
                this.prefetchedAlbum = data;
            })
            .catch(() => {
                this.prefetchedAlbum = null;
            });
    }

    async getAlbumWithPrefetch() {
        if (this.prefetchedAlbum) {
            const album = this.prefetchedAlbum;
            this.prefetchedAlbum = null;
            this.prefetchNextAlbum();
            return album;
        }

        if (this._prefetchPromise) {
            await this._prefetchPromise;
            if (this.prefetchedAlbum) {
                const album = this.prefetchedAlbum;
                this.prefetchedAlbum = null;
                this.prefetchNextAlbum();
                return album;
            }
        }

        const response = await this.get_spotify_random_album();
        const album = await response.json();
        this.prefetchNextAlbum();
        return album;
    }

    login_spotify() {
        const current_url = window.location.host;
        const scopes = 'user-library-read';
        const vars = this.get_spotify_env_vars()
        const redirect_uri = `${vars.API_ENDPOINT_URI}/spotifyauth`;
        const url = `https://accounts.spotify.com/authorize?response_type=code&client_id=${vars.SPOTIFY_APP_ID}&scope=${encodeURIComponent(scopes)}&redirect_uri=${encodeURIComponent(redirect_uri)}&return_to=${encodeURIComponent(current_url)}`;
        window.location.href = url;
    }

    get_spotify_env_vars() {
        const host = window.location.host.toLowerCase();
        const spotify_app_id = '50282a1aed904387aba31b12b9a33050';
        // Localhost
        if (host.includes('lvh.me') || host.includes('localhost')) {
          return {
            API_ENDPOINT_URI: "https://api-dev.albumshuffler.com",
            SPOTIFY_APP_ID: spotify_app_id
          }
        }
        // Dev
        else if (host.includes('PUT DEV URLS HERE')) {
          return {
            API_ENDPOINT_URI: "https://api-dev.albumshuffler.com",
            SPOTIFY_APP_ID: spotify_app_id
          }
        }
        // Production
        else if (host.includes('albumshuffler.com')) {
          return {
            API_ENDPOINT_URI: "https://api.albumshuffler.com",
            SPOTIFY_APP_ID: spotify_app_id
          }
        }
      }

      get_spotify_random_album() {
        const vars = this.get_spotify_env_vars();
        const token = localStorage.getItem('albumShuffler.spotify.authToken');
        if (token == null) {
          this.login_spotify()
        }
        else {
          return fetch(`${vars.API_ENDPOINT_URI}/randomalbum`,
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + token,
            }
          });
        }
        
      }

      maybe_refresh_albums() {
        const vars = this.get_spotify_env_vars();
        const token = localStorage.getItem('albumShuffler.spotify.authToken');
        const lastRefresh = localStorage.getItem('albumShuffler.spotify.lastRefresh');
        
        let refreshNeeded = false;
        if (lastRefresh === null) {
          refreshNeeded = true;
        }
        else {
          const lastRefreshDiff = Math.abs(new Date() - new Date(lastRefresh)) / 36e5;
          refreshNeeded = lastRefreshDiff >= 24;
        }
        
        if (refreshNeeded) {
          localStorage.setItem('albumShuffler.spotify.lastRefresh', new Date().toISOString())
          return fetch(`${vars.API_ENDPOINT_URI}/refresh`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + token,
            }, 
          });
        }
      }
}

export { AlbumShufflerApi }