import React from "react";

import { INTERVALS } from "../../../common/constants";

const TimeStepPickerComponent = props => (
  <select
    value={props.currentTimeStep}
    onChange={props.onTimeStepChange}
    className="form-control"
  >
    {INTERVALS.map((interval, index) => (
      <option key={index} value={interval.value}>
        {interval.verbose}
      </option>
    ))}
  </select>
);

export default TimeStepPickerComponent;
