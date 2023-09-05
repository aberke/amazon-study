// utilities

// Qualtrics API
const DATACENTERID = 'iad1';
const BASE_URL = `https://${DATACENTERID}.qualtrics.com/API`;
// DO NOT commit the API token to github
// In Qualtrics surveys we use embedded data to store/access the value.
// For local development: Can use as an environment variable.
const API_TOKEN = '';

const apiGET = function(endpoint) {
    endpoint = endpoint || 'whoami';
    let url = `${BASE_URL}/v3/${endpoint}`;
    const headers = new Headers({
        "x-api-token": API_TOKEN,
    });
    const request = new Request(url, {
        method: 'GET',
        headers: headers,
        mode: 'cors',
        cache: 'default',
    });
    console.log('apiGET', url, request)
    fetch(request)
    .then(response => response.json())
    .then(data => {
        console.log(data); 
        return data;
    });
}

const apiGetSurveyResponse = async function(surveyID, responseID) {
    const endpoint = `surveys/${surveyID}/responses/${responseID}`;
    let resp = apiGET(endpoint)
    console.log('resp', resp);
    return resp;
}



// For later: something that can help verify same data not uploaded twice
function getDataHash(csvData) {
    // csvData is already reduced to what will be shown/collected
    // Ideal hash / ID should 
    // - not re-identify the user more than their data already can
    // - be based on the data in the way that duplicate uploads can
    //  be identified and avoided.
    // - should only use data included in minimal csvData
    //      (e.g. avoid using category or title)
    // - should be robust against changes to how Amazon exports data
    // - should be robust against our implementation changes
    //      (e.g. avoid using price since there are multiple price field and which we choose now is subj to change)
    // - low collision probabily between different participants
    // ideas for how to do this:
    // choose dates subset: e.g. Jan 1 2019 - Dec 31 2021
    // make {date}{zip5} pairs for each order. sort as list.
    // hash the value
    
    // get data subset to use: only use data between dStart and dEnd
    // make sure there is a zip code
    const dStart = new Date('01/01/2019');
    const dEnd = new Date('12/31/2021');
    const filterRowByDate = function(row) { 
        const d = new Date(row['Order Date']);
        return (dStart <= d) && (d <= dEnd);
    }
    let dataSubset = csvData.filter(filterRowByDate);
    dataSubset = dataSubset.filter(row => (row['Shipping Address Zip'].length >= 5));
    // sorted list of strings where each is concatenation of {OrderDate}{Zip5}
    let rowStrings = dataSubset.map(row => (new Date(row['Order Date']).toISOString()+row['Shipping Address Zip'].slice(0,5)));
    rowStrings.sort();
    function simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
          const char = str.charCodeAt(i);
          hash = (hash << 5) - hash + char;
          hash &= hash; // Convert to 32bit integer
        }
        return new Uint32Array([hash])[0].toString();
    };
    return simpleHash(rowStrings.toString()).slice(0, idLength).padEnd(idLength, 0);
}
