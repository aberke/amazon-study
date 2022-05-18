"use strict";

/*
The following Javascript assumes that the questions in qualtrics
have been set up as described in the README.
namely:
- set needed embedded data
- recode question choie values

The javascript must be inserted into the Qualtrics Questions JS
interface for each question it is to be called.
However, in order to make this easier to copy, test, track, use
outside of qualtrics (e.g. testing standalone HTML pages),
we extract this as a small javascript (here).
There are some strange choices made to accomodate for Qualtrics.

Basic steps:

Retrieve embedded data:
- API_TOKEN
- SurveyID
- ResponseID
- FQID (question id for file upload question)

show file input and attach listeners

(If in qualtrics)
- hide the questions
- disable 'next'
- add listeners for qualtrics events

Upon file input
- handle file and display in browser, based on version
- show questions/other hidden text

Upon file share (if in qualtrics and if consent):
- POST new survey response via Qualtrics API with just the file as the content.

*/

let qualtricsDeclared; 
try {
    Qualtrics;
    qualtricsDeclared = true;
} catch(e) {
    qualtricsDeclared = false;
}
console.log(qualtricsDeclared ? 'Qualtrics' : 'Test without Qualtrics');

// Note: Qualtrics makes the embedded data available via the 
// Qualtrics.SurveyEngine.getEmbeddedData
// EXCEPT for ResponseID. Must get this via the piped text feature.
function getResponseId() {
    return (!qualtricsDeclared) ? 'TEST_ResponseID' : "${e://Field/ResponseID}"; //Qualtrics.SurveyEngine.getEmbeddedData('ResponseID');
}
function getSurveyId() {
    return (!qualtricsDeclared) ? 'TEST_SurveyID' : Qualtrics.SurveyEngine.getEmbeddedData('SurveyID');
}
function getApiToken() {
    return (!qualtricsDeclared) ? 'TEST_API_TOKEN' : Qualtrics.SurveyEngine.getEmbeddedData('API_TOKEN');
}
function getFQID() {
    return (!qualtricsDeclared) ? 'TEST_FQID' : Qualtrics.SurveyEngine.getEmbeddedData('FQID');
}
const responseId = getResponseId();
const surveyId = getSurveyId();
const API_TOKEN = getApiToken();
const FQID = getFQID();
const DATACENTERID = 'iad1';
// Note string interpolation with ` and $ not supported in qualtrics JS.
const BASE_URL = 'https://' + DATACENTERID + '.qualtrics.com/API';

console.log('using responseId:', responseId, 'surveyId:', surveyId, 
            'FQID:', FQID, 'BASE_URL:', BASE_URL);


function getUrlParams(url) {
    if(!url) url = location.search;
    let query = url.substr(1);
    let result = {};
    query.split("&").forEach(function(part) {
        let item = part.split("=");
        result[item[0]] = decodeURIComponent(item[1]);
    });
    return result;
}


/*
CSV data handling
Parsing the CSV using Papa Parse 5:
https://www.papaparse.com/docs
*/
let csvData = null;
const defaultDataVersion = 'B';
const dataVersionKey = 'data';
function getDataVersion() {
    let urlParams = getUrlParams();
    return urlParams[dataVersionKey] || defaultDataVersion;
}
let dataVersion = getDataVersion();
console.log('using data version:', dataVersion);

// Data columns to use:
// version A: partial data
let csvColumnsVersionA = [
    'Order Date',
    'Purchase Price Per Unit',
    'Quantity',
    'Shipping Address Zip', // Address info unavailable for items shipped to Amazon Lockers
];
// version B: granular data
let csvColumnsVersionB = csvColumnsVersionA.concat([
    'Title',
    'ASIN/ISBN',
    'Category',
]);
let csvColumns = (dataVersion === 'A' ? csvColumnsVersionA : csvColumnsVersionB);

const responseIdCol = 'Survey ResponseID';
const currencyCol = 'Currency';


function filterRow(row) {
    // Returns whether row passes the filter test.
    // filter out non-US orders and returned orders (quantity 0)
    // TODO: also use 'Shipping Address Zip' (or another col)
    //       to skip non US orders
    if (row[currencyCol] !== 'USD') {
        console.log('filtering row with non-US currency:', row[currencyCol])
        return false;
    }
    if (row['Quantity'] < 1) {
        console.log('filtering row with Quantity', row['Quantity'])
        return false;
    }
    return true;
}

function filterColumns(rowObj, keepCols) {
    return Object.assign({}, ...keepCols.map(k => ({ [k]: rowObj[k] })))
}

function reduceCsvData(data, columns) {
    // filter out some rows
    data = data.filter(filterRow);
    // keep only the desired columns
    data = data.map(row => filterColumns(row, columns));
    return data;
}

function addResponseId(data, responseIdCol, responseId) {
    // add the key: value for each item in the array
    // would prever to do it this way:
    //return data.map((row => ({...row, [responseIdCol]: responseId})));
    // qualtrics embedded JS way: (qualtrics doesn't support ...)
    function addId(obj) {
        obj[responseIdCol] = responseId;
        return obj;
    }
    return data.map(addId);
}

function handleFileInput(e) {
    Papa.parse(e.target.files[0], {
        header: true,
        complete: function(results) {
            console.log('TODO: validate file input')
            // build the csvData
            // data is an array of dicts where each dict maps column to value
            // [{col: val, for col,val in row} for row in csvData]
            // create a reducedData object (array) with the same data structure
            csvData = reduceCsvData(results.data, csvColumns);
            // add in the participant ID
            const responseId = getResponseId(csvData);
            csvData = addResponseId(csvData, responseIdCol, responseId);
            let columns = [responseIdCol].concat(csvColumns);
            // build the table to show
            buildTable(csvData, columns);
            showChoices();
            shareDataLanguageContainer.style.display = 'block';
        }
    });
}

function buildTable(csvData, columns) {
    // clear out (possibly) previously inserted table
    tableContainerElt.innerHTML = "";
    // build new data
    let totalRows = csvData.length;
    let totalRowsP = document.createElement('p');
    totalRowsP.appendChild(document.createTextNode(totalRows.toString() + ' rows (scroll)'));
    tableContainerElt.appendChild(totalRowsP);

    let tableElt = document.createElement('table');
    var tableBodyElt = document.createElement('tbody');
    // create header
    let headerRowElt = document.createElement('tr');
    columns.forEach(col => {
        let cell = document.createElement('th');
        cell.appendChild(document.createTextNode(col));
        headerRowElt.appendChild(cell);
    });
    tableBodyElt.appendChild(headerRowElt);
    // create table rows
    csvData.forEach(row => {
        let rowElt = document.createElement('tr');
        // maintain consistent column order with header
        columns.forEach(col => {
            let cell = document.createElement('td');
            cell.appendChild(document.createTextNode(row[col]));
            rowElt.appendChild(cell);
        });
        tableBodyElt.appendChild(rowElt)
    });
    tableElt.appendChild(tableBodyElt);
    tableContainerElt.appendChild(tableElt);
}

// qualtrics JS parser doesn't allow async 
// async function createSurveyResponseForFile(surveyId, responseId, f, fQID) {
function createSurveyResponseForFile(surveyId, responseId, f, fQID) {
    /*
    Note: this is a messy hack of a way to integrate the questions API with the 
    other qualtrics API in order to upload files from the survey for the respondent.
    Creates a new survey response for the file uploaded by the respondant with
    responseId.
    This is a *separate* response where the only response value is the file.
    The fileQID is the QID for an invisible file upload field.
    We use the responseId for the current survey taker as both the 
    upload file name and idempotency-key (upload it once)

    Uses the create new survey response API endpoint:
    https://api.qualtrics.com/f1cad92018d2b-create-a-new-response
    */
    let fname = String(responseId) + '.csv'; // qualtrics: avoid using smart quotes
    let formData = new FormData();
    formData.append("response", JSON.stringify({values:{}})); // required
    formData.append("fileMapping", JSON.stringify({file1: fQID}));
    formData.append("file1", f, fname); // use the respondId as the upload filename
    const url = BASE_URL + '/v3/surveys/' + String(surveyId) + '/responses';
    console.log('created survey response for file with POST to url', url);
    return fetch(url, {
        method: "POST",
        headers: {
            // Despite the API documentation: leave "Content-Type" undefined/empty
            // and let browser determine content-type header value
            // The reason is that a 'boundary' value must be inserted and the browser can best do this.
            //"Content-Type": undefined, //"multipart/form-data", 
            // Using Idempotency-Key to ensure only one file upload per responseId
            // Must use No value or different idempotency-key to create new responses!
            "Idempotency-Key": responseId, 
            "X-API-TOKEN": API_TOKEN,
        },
        body: formData
    }) // yes using arrows would be nice, but not supported by qualtrics JS parser
    .then(function(response) { return response.json() })
    .then(function(result) { console.log('result:', result); return result.result; })
    .catch(function(err) { console.log('error:', err); return err; } );
}

function uploadProcessedCsvData() {
    // make the csvDatafile
    let csv = Papa.unparse(csvData);
    let csvBlob = new Blob([csv], {type:"text/csv"});
    let surveyId = getSurveyId();
    let responseId = getResponseId();
    createSurveyResponseForFile(surveyId, responseId, csvBlob, FQID)
    .then(function(result) {
        console.log('created survey response for file returned result', result);
    });
}

const shareDataLanguageContainer = document.getElementById('share-data-language-container');
shareDataLanguageContainer.style.display = 'none';

const tableContainerElt = document.getElementById('purchases-data-table-container');
const fileInput = document.getElementById('file-input');
fileInput.addEventListener('change', handleFileInput);

// might also use surveyEngine.choiceContainer
let choiceContainerSelector = qualtricsDeclared ? '.QuestionBody' : '.test-choice-container'; // using class for testing to be consistent with qualtrics
let showChoices = function() {
    document.querySelectorAll(choiceContainerSelector).forEach(function(el) {
        el.style.display = 'block';
     });
}
let hideChoices = function() {
    document.querySelectorAll(choiceContainerSelector).forEach(function(el) {
        el.style.display = 'none';
     });
}

if (qualtricsDeclared) {
    let surveyEngine = this;
    console.log('surveyEngine:', surveyEngine);
    
    function disableNext() {
        surveyEngine.disableNextButton();
    }
    function enableNext() {
        surveyEngine.enableNextButton();
    }
    hideChoices();
    disableNext();

    let uploadConsent = false;
    surveyEngine.questionclick = function(event, element){
        console.log('surveyEngine.questionclick', event, element)
        //for a single answer multiple choice question, the element type will be radio
        // the consent/decline questions are consistently recoded (TODO: ensure this)
        // consent: value=1; decline:value=0
        if (element.type == 'radio') {
            let choiceId = element.id.split('~')[2];
            let choiceRecodeValue = surveyEngine.getChoiceRecodeValue(choiceId);
            if (choiceRecodeValue === '1') {
                uploadConsent = true;
            } else {
                uploadConsent = false;
            }
            console.log('set upload consent to ', uploadConsent);
            enableNext();
        }
    }

    Qualtrics.SurveyEngine.addOnPageSubmit(function(type) {
        console.log('OnPageSubmit with type', type);
        if (type !== 'prev') {
            if (uploadConsent == true) {
                uploadProcessedCsvData();
            }
        }
    });

    console.log('Qualtrics script bottom')
}

console.log('script bottom');