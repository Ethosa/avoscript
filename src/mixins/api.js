const API_DOMEN = "localhost:8000"
const API_URL = `http://${API_DOMEN}/`

/**
 * Sends request
 * @param {String} url
 * @param {Dict} data
 */
async function post(url, data) {
    data.method = 'POST'
    data.headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    const req = await fetch(url, data);
    return await req.json();
}


export default {
    async exec(code) {
        return await post(`${API_URL}exec`, {
            body: JSON.stringify({
                'value': code
            })
        })
    }
}
