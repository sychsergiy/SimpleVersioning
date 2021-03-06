import React, { Component } from "react";
import { connect } from "react-redux";

import { setTargetOption } from "../../options/actions";

import {
  selectProjectFilter,
  unSelectProjectFilter
} from "../actions/selections";

import { separateSelectedItems } from "../../../common/filtersHelper/common";

import { billingTargetTypes } from "../../../common/constants";

import BaseFilterContainer from "./BaseFilter";

const mapStateToProps = state => {
  let [selectedProjects, unSelectedProjects] = separateSelectedItems(
    state.billing.filters.hierarchy.projects,
    state.billing.filters.selections.projects
  );
  return {
    selectedItems: selectedProjects,
    visibleItems: unSelectedProjects,
    currentTargetType: billingTargetTypes.project,
    selectedTargetType: state.billing.options.targetType,
    selectedTargetIDs: state.billing.options.targetIDs,
    blockTitle: "Projects",
    blockTitleIconClass: "fas fa-project-diagram mr-2",
    loading: state.billing.filters.hierarchy.loading,
    error: state.billing.filters.hierarchy.error
  };
};

const mapDispatchToProps = dispatch => ({
  selectFilterItem: projectID => {
    dispatch(selectProjectFilter(projectID));
  },
  unSelectFilterItem: projectID => {
    dispatch(unSelectProjectFilter(projectID));
  },
  selectTarget: targetID => {
    dispatch(setTargetOption(targetID, billingTargetTypes.project));
  }
});

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(BaseFilterContainer);
