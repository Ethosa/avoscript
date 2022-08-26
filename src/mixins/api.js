const API_DOMEN = "avoscript.herokuapp.com"
const API_URL = `https://${API_DOMEN}/`

/**
 * Sends POST request
 * @param {String} url
 * @param {Dict} data
 */
async function post(url, data) {
  data.method = 'POST'
  data.headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
  const req = await fetch(url, data)
  return await req.json()
}

/**
 * Sends GET requests
 * @param {String} url
 */
async function get(url) {
  const req = await fetch(url)
  return await req.json()
}


export default {
  /**
   * Executes code
   * @param {String} code 
   * @returns output
   */
  async exec(code) {
    return await post(`${API_URL}exec`, {
      body: JSON.stringify({
        value: code
      })
    })
  },
  async save(code) {
    return await post(`${API_URL}save`, {
      body: JSON.stringify({
        value: code
      })
    })
  },
  async load(uuid) {
    return await get(`${API_URL}code/${uuid}`)
  },
  async version() {
    return await get(`${API_URL}version`)
  }
}
