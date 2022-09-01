export default {
  async fetchPackages() {
    const req = await fetch('https://raw.githubusercontent.com/Ethosa/avoscript/master/pkgs.json')
    const data = await req.json()
    return data
  },
  async fetchReadme(url) {
    const req = await fetch(this.githubUrlToRawUserContent(url) + '/master/README.md')
    const data = await req.text()
    console.log(data)
    return data
  },
  /**
   * @param {String} url
   */
  githubUrlToRawUserContent(url) {
    return url.replace('github.com', 'raw.githubusercontent.com')
  }
}