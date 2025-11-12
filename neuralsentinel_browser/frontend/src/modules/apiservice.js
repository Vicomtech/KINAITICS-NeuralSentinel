class APIService {

  /**
   * @param {String} url request url
   * @param {String} method request method
   * @param {{String:String}} headers Additional headers for the request
   * @param {{String:String}} args Args for the request if needed
   * @param {{String:any}} body The body of the request if needed
   * @param {"file"|"json" } returnType Return type of the function. if file it would return a blob. JSON otherwise
   */
  async execute(url, method, headers={},args={},body=null, returnType="json") {
    try {
      if (Object.keys(this.requestdict).includes(request)) {
        let hds = {'Access-Control-Expose-Headers': 'Content-Disposition', ...headers}
        if (Object.keys(args).length > 0) {
          let keys = Object.keys(args)
          url += `?${keys[0]}=${args[keys[0]]}`
          keys.shift()
          for (let k of keys) {
            url += `&${k}=${args[k]}`
          }
        }
        let response = null
        if (body) {
          response = await fetch(url,
            {
              method: method,
              headers: hds,
              body: body,
            }
          );
        } else {
          response = await fetch(url,
            {
              method: method,
              headers: hds
            }
          );
        }
        if (!response.ok) {
          throw new Error(`${response.status}: ${response.statusText}`);
        }
        if (returnType == "json") {
          const jsn = await response.json()
          return jsn
        } else {
          const fl =  await response.blob()
          return fl;
        }
      }
      else {
        throw new Error(`Unable to perform ${request}. Unknown request`);
      }
    } catch (error) {
      throw new Error(`ERROR: ${error}`);
    }
  }
}

const api = new APIService()
export default api