const express = require('express');
const app = express();
const port = process.env.PORT || 3000;
const Cloudant = require('@cloudant/cloudant');
const fs = require('fs');
const creds = JSON.parse(fs.readFileSync('../../.creds.json', 'utf8'));

async function dbCloudantConnect() {
    try {
        const cloudant = Cloudant({
            plugins: { iamauth: { iamApiKey: creds.IAM_API_KEY } },
            url: creds.COUCH_URL,
        });
        const db = cloudant.use('dealerships');
        console.info('Connect success! Connected to DB');
        return db;
    } catch (err) {
        console.error('Connect failure: ' + err.message + ' for Cloudant DB');
        throw err;
    }
}

let db;
(async () => {
    db = await dbCloudantConnect();
})();

app.use(express.json());

app.get('/api/dealership', (req, res) => {
    let { state } = req.query;
    const selector = {};

    if (state) {
        state = state.replace(/"/g, '');
        selector.state = state;
    }

    console.log(req.query);
    console.log(state);

    const queryOptions = {
        selector,
        limit: 10,
    };

    db.find(queryOptions, (err, body) => {
        if (err) {
            console.error('Error fetching dealerships:', err);
            return res.status(500).json({ error: 'Something went wrong on the server' });
        } else if (body.docs.length === 0) {
            if (state) {
                return res.status(404).json({ error: 'The state does not exist'  });
            } else {
                return res.status(404).json({ error: 'The database is empty' });
            }
        } else {
            return res.json(body.docs);
        }
    });
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
