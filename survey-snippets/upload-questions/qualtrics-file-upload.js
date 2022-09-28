"use strict";

/*
The following Javascript assumes that the questions in qualtrics
have been set up as described in the README.
namely:
- set needed embedded data
- recode question choice values

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
- disable 'next'
- add listeners for qualtrics events

Upon file input
- handle file and display in browser, based on version
- show questions/other hidden text

Upon file share (if in qualtrics and if consent):
- POST new survey response via Qualtrics API with just the file as the content.

Note the additional quirks: 
- sometimes the Qualtrics API prefers being called
via this. Sometimes via Qualtrics.SurveyEngine

*/

let qualtricsDeclared;
let surveyEngine;
try {
    Qualtrics;
    qualtricsDeclared = true;
    surveyEngine = this;
} catch(e) {
    qualtricsDeclared = false;
}
console.log(qualtricsDeclared ? 'Qualtrics' : 'Test without Qualtrics');

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

function getEmbeddedShowData() {
    // Returns Boolean or undefined
    if (!!qualtricsDeclared) {
        let embeddedShowData = Qualtrics.SurveyEngine.getEmbeddedData('showdata');
        if (embeddedShowData === 'true' || embeddedShowData === true) {
            return true;
        } else if (embeddedShowData === 'false' || embeddedShowData === false) {
            return false;
        }
    }
}
// For the following, the embedded data value can be overridden
// by URL parameters.
let showDataDefault = true; // default
function getShowData() {
    let showData = getEmbeddedShowData();
    // URL parameter (can override embedded data)
    let urlParamShowData = getUrlParams()['showdata'];
    if (urlParamShowData==='false') {
        showData = false;
    } else if (urlParamShowData==='true') {
        showData = true;
    }
    return (showData===undefined) ? showDataDefault : showData;
}
const showData = getShowData();
console.log('showdata=', showData);


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
    'Shipping Address State', // Address info unavailable for items shipped to Amazon Lockers
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

// Rename some CSV column names to improve clarity
const csvColumnNameMap = {
    'ASIN/ISBN': 'ASIN/ISBN (Product Code)',
};

let displayColumns = [responseIdCol].concat(csvColumns).map( c => csvColumnNameMap[c] || c );


function filterRow(row) {
    // Returns whether row passes the filter test.
    // filter out non-US orders and returned orders (quantity 0)
    // TODO?: also use 'Shipping Address __' to skip non US orders ?
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

function validateCsvData(csvData) {
    // Check there is at least 2 rows of data with expected columns.
    if (csvData.length < 2) {
        return {
            data: csvData,
            message: 'Missing data. Is this the right file?'
        };
    }
    // Check there is data dating back to 2018.
    const orderDateYears = new Set(csvData.map(rowObj => new Date(rowObj['Order Date']).getFullYear()));
    if (!orderDateYears.has(2018)) {
        return {
            data: csvData,
            message: 'Missing data from 2018.'
        };
    }
    // Check there are multiple years of data.
    // We ask for 2018 - 2021 data (4 years). Be flexible. Maybe they went a year abroad.
    if (orderDateYears < 2) {
        return {
            data: csvData,
            message: 'Missing multiple years of data.'
        };
    }
}
let errorMessageP = document.getElementById('error-message');
function displayErrorMessage(errMessage) {
    let displayMessage = "There is a problem with the file: ";
    displayMessage += errMessage;
    displayMessage += "\nPlease try the data download process again and choose the new file.";
    displayMessage += "\nYou can click back to the previous page to report an issue.";
    errorMessageP.innerHTML = displayMessage;
    errorMessageP.style.display = 'block';
}
function hideErrorMessage() {
    errorMessageP.style.display = 'none';
}

function mapCsvDataColumnNames(data, nameMap) {
    function mapNames(rowObj) {
        let newRowObj = {};
        Object.keys(rowObj).map((c) => newRowObj[(nameMap[c]||c)] = rowObj[c]);
        return newRowObj;
    }
    return data.map(mapNames);
}

function handleFileInput(e) {
    // Hide the possibly previously shown error message.
    hideErrorMessage();
    // clear out possibly previous set data
    validFile = false;
    disableNext();
    Papa.parse(e.target.files[0], {
        header: true,
        complete: function(results) {
            // data is an array of dicts where each dict maps column to value
            // [{col: val, for col,val in row} for row in csvData]
            // create a reducedData object (array) with the same data structure
            csvData = reduceCsvData(results.data, csvColumns);
            const validationError = validateCsvData(csvData);
            if (!!validationError) {
                console.log('File validation failed:', validationError);
                displayErrorMessage(validationError.message);
            } else {
                // build the csvData
                // add in the participant ID
                const responseId = getResponseId(csvData);
                csvData = addResponseId(csvData, responseIdCol, responseId);
                // Update any column names
                csvData = mapCsvDataColumnNames(csvData, csvColumnNameMap);
                if (showData) {
                    // In case the respondent previously inserted a file that passed validation:
                    // Clear out (possibly) previously inserted data.
                    dataContainerElt.innerHTML = "";
                    // build the table to show
                    buildTable(csvData, displayColumns);
                }
                showChoices();
                showShareDataLanguage();
                validFile = true;
                checkEnableNext();
            }
        }
    });
}

function buildDataDescription() {
    let ul = document.createElement('ul');
    displayColumns.forEach(function(c) {
        let li = document.createElement('li');
        li.appendChild(document.createTextNode(c));
        ul.appendChild(li);
    });
    dataContainerElt.appendChild(ul);
}

function buildTable(csvData, columns) {
    // build new data
    let totalRows = csvData.length;
    let totalRowsP = document.createElement('p');
    totalRowsP.appendChild(document.createTextNode(totalRows.toString() + ' rows (scroll)'));
    dataContainerElt.appendChild(totalRowsP);

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
    dataContainerElt.appendChild(tableElt);
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

const shareDataLanguageContainerSelector = '.share-data-language-container';
let showShareDataLanguage = function() {
    document.querySelectorAll(shareDataLanguageContainerSelector).forEach(function(el) {
        el.style.display = 'block';
     });
}
let hideShareDataLanguage = function() {
    document.querySelectorAll(shareDataLanguageContainerSelector).forEach(function(el) {
        el.style.display = 'none';
     });
}

const dataContainerElt = document.getElementById('purchases-data-container');
buildDataDescription();

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
showChoices();

// Flow logic
let validFile = false;
let choiceSelected = false;

let disableNext = function() {
    if (!qualtricsDeclared) {
        return console.log('disableNext');
    }
    surveyEngine.disableNextButton();
}
let enableNext = function() {
    if (!qualtricsDeclared) {
        return console.log('enableNext');
    }
    surveyEngine.enableNextButton();
}
disableNext();

function checkEnableNext() {
    if (!!validFile & !!choiceSelected) {
        enableNext();
    }
}

if (qualtricsDeclared) {
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
            choiceSelected = true;
            console.log('set upload consent to ', uploadConsent);
            checkEnableNext();
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
