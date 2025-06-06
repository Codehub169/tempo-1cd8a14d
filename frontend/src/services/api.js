import axios from 'axios';

const API_BASE_URL = '/api'; // Proxy will redirect this to backend (e.g., http://localhost:9000/api)

/**
 * Fetches video information from YouTube.
 * @param {string} url The YouTube video URL.
 * @returns {Promise<object>} A promise that resolves to the video information.
 */
export const fetchYouTubeInfo = async (url) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/youtube/info`, {
      params: { url },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching YouTube info:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Failed to fetch YouTube video information');
  }
};

/**
 * Initiates a download for YouTube media (video or audio).
 * @param {string} url The YouTube video URL.
 * @param {string} formatId The format ID of the media to download.
 * @param {string} type 'video' or 'audio'.
 * @param {string} filename Suggested filename for the download.
 * @returns {Promise<Blob>} A promise that resolves to the media file blob.
 */
export const downloadYouTubeMedia = async (url, formatId, type, filename) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/youtube/download`, {
      params: { url, format_id: formatId, type },
      responseType: 'blob', // Important for file download
    });
    
    // Create a link and trigger download
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', filename || `${type}_${formatId}.mp4`); // Use provided filename or generate one
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);

    return response.data; // Or true if just confirming initiation
  } catch (error) {
    console.error('Error downloading YouTube media:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Failed to download YouTube media');
  }
};

/**
 * Fetches reel information from Instagram.
 * @param {string} url The Instagram reel URL.
 * @returns {Promise<object>} A promise that resolves to the reel information.
 */
export const fetchInstagramInfo = async (url) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/instagram/info`, {
      params: { url },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching Instagram info:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Failed to fetch Instagram reel information');
  }
};

/**
 * Initiates a download for an Instagram reel.
 * @param {string} url The Instagram reel URL.
 * @param {string} filename Suggested filename for the download.
 * @returns {Promise<Blob>} A promise that resolves to the reel file blob.
 */
export const downloadInstagramReel = async (url, filename) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/instagram/download`, {
      params: { url },
      responseType: 'blob',
    });

    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', filename || 'instagram_reel.mp4');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);

    return response.data;
  } catch (error) {
    console.error('Error downloading Instagram reel:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Failed to download Instagram reel');
  }
};
