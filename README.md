# **Microservices & Cloud Computing Final Project** 
##### Paige Rosynek
##### CSC 5201 301
##### 05.03.2024

---

# **Wrapify - Spotify Listening History Summary**


## **Description**

Wrapify is an application that allows users to summarize their listening habits on Spotify over varying time frames. This application was inspired by the annual Spotify Wrapped which at the end of the year, provides users with a fun and insightful report of their listening habits on the app over the last year with information on the number of minutes listened, top tracks, and much more. Wrapify is a simplified version of this. With Wrapify a user can login with their Spotify account to generate, save, and delete summaries of their listening habits all year round. Each summary consists of information on the user's top 10 tracks, top 10 artists, and top 5 genres for the specified time frame. There are 3 time frames a wrap can be generated for: short (last ~4 weeks), medium (last ~6 months), long (last ~1 year). Each wrap generated is stored in a MongoDB database and users can view and delete their past wraps from within the application. With Wrapify, users can get insight into their music taste year-round!

## **Installation**

The application is deployed on a DigitalOcean Droplet running at `http://146.190.166.177:5000` so no further installation is needed.



### Run Locally (Docker-Compose)

To run the application locally:

1. Clone this repo using `git clone`
2. Navigate to the `authentication_service.py` file in the `auth_service` directory
3. Uncomment the `REDIRECT_URI` constant at the top of the file to `http://localhost:5000` and save
4. In the project root directory, run:
- `docker-compose build`
- `docker-compose up -d`

5. Enter `http://localhost:5000` in your browser to access the running application
6. To stop the application run: `docker-compose down`

**NOTE**
Due to Spotify's developer restrictions, in order to log into the application your Spotify email must be whitelisted. Optionally you can follow the steps to retrieve your own Spotify client credentials at the link here: `https://developer.spotify.com/documentation/web-api/concepts/apps` and replace the CLIENT_ID and CLIENT_SECRET variables in the config.py file in the auth_service directory.


## **Documentation & Use Cases**

### **Endpoints**

#### `/`
**Method:** `GET`

**Description:** Renders the home page of the application.

#### `/login`
**Method:** `GET`

**Description:** Initiates the authentication process with Spotify OAuth. Communicates with the authentication service to retrieve an authorization URL from Spotify and redirects the user.


#### `/callback`
**Method:** `GET`
**Description:** 
