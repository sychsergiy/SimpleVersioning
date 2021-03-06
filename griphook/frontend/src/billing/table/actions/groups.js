import * as types from "../actionTypes";

export const selectBillingTableRow = servicesGroupID => ({
  type: types.SELECT_BILLING_TABLE_ROW,
  servicesGroupID
});

export const unSelectBillingTableRow = () => ({
  type: types.UNSELECT_BILLING_TABLE_ROW
});

export const fetchBillingTableDataBegin = () => ({
  type: types.FETCH_BILLING_TABLE_DATA_BEGIN
});

export const fetchBillingTableDataSuccess = data => ({
  type: types.FETCH_BILLING_TABLE_DATA_SUCCESS,
  data
});

export const fetchBillingTableDataFailure = error => ({
  type: types.FETCH_BILLING_TABLE_DATA_FAILURE,
  error
});

export const setBillingTablePageNumber = pageNumber => ({
  type: types.SET_BILLING_TABLE_PAGE_NUMBER,
  pageNumber
});

export const fetchBillingTableData = options => dispatch => {
  dispatch(fetchBillingTableDataBegin());
  const data = {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(options)
  };
  return fetch("/api/billing/get_filtered_table_data", data)
    .then(handleErrors)
    .then(response => response.json())
    .then(json => {
      dispatch(fetchBillingTableDataSuccess(json));
      return json;
    })
    .catch(error => dispatch(fetchBillingTableDataFailure(error)));
};

function handleErrors(response) {
  if (!response.ok) {
    throw Error(response.statusText);
  }
  return response;
}
