import express from 'express';
import dotenv from 'dotenv';
import axios from 'axios';


const fetchUserId  = async (username) => {

    const fetchIdResponse = await axios.get(`${process.env.SERVER_URL}/user/fetchID/${username}`);
    if (!fetchIdResponse.data.success) {
        return res.status(404).json({
            success: false,
            message: 'User not found'
        });
    }

    return fetchIdResponse.data.userId;
}

export default fetchUserId;
