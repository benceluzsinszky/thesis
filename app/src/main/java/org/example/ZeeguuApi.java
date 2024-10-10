package org.example;

import java.io.OutputStream;
import java.io.InputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

public class ZeeguuApi {

    public static void main(String[] args) {
        String url = "https://api.maxitwit.tech/session/bluz@itu.dk";
        String password = "password";
        String session = getUserSession(url, password);
        String activityUrl = "https://api.maxitwit.tech/upload_user_activity_data";
        uploadUserActivityData(activityUrl, session);
    }

    public static String getUserSession(String urlString, String password) {
        HttpURLConnection connection = null;
        String session = null;
        try {
            URL url = new URL(urlString);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; utf-8");
            connection.setRequestProperty("Accept", "application/json");
            connection.setDoOutput(true);

            String urlParameters = "password=" + URLEncoder.encode(password, StandardCharsets.UTF_8.toString());

            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = urlParameters.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            int code = connection.getResponseCode();
            System.out.println("Response Code: " + code);

            InputStream is;
            if (code >= 200 && code < 300) {
                is = connection.getInputStream();
            } else {
                is = connection.getErrorStream();
            }

            try (BufferedReader br = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = br.readLine()) != null) {
                    response.append(responseLine.trim());
                }

                String responseString = response.toString();
                session = responseString.substring(responseString.indexOf(":\"") + 2,
                        responseString.lastIndexOf("\""));

                // System.out.println(session);
                return session;
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (connection != null) {
                connection.disconnect();

            }
        }
        return session;
    }

    public static void uploadUserActivityData(String urlString, String session) {
        String jsonBody = "{"
                + "\"time\": \"2016-05-05T10:11:12\","
                + "\"event\": \"User Read Article\","
                + "\"value\": \"300s\","
                + "\"extra_data\": {"
                + "\"article_source\": 2"
                + "}"
                + "}";
        HttpURLConnection connection = null;
        try {
            URL url = new URL(urlString + "?session=" + session);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json; utf-8");
            connection.setRequestProperty("Accept", "application/json");
            connection.setDoOutput(true);

            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = jsonBody.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }
            int code = connection.getResponseCode();
            System.out.println("Response Code: " + code);

            InputStream is;
            if (code >= 200 && code < 300) {
                is = connection.getInputStream();
            } else {
                is = connection.getErrorStream();
            }

            try (BufferedReader br = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = br.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                System.out.println("Response: " + response.toString());
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }

    }

}