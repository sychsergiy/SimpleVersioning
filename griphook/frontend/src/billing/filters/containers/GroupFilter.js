import React, { Component } from "react";
import { connect } from "react-redux";

import {
  setTargetOption,
  addGroupToTargetIDs,
  removeGroupFromTargetIDs
} from "../../options/actions";

import { getFilteredServicesGroups } from "../../../common/filtersHelper/servicesGroups";
import { separateSelectedItems } from "../../../common/filtersHelper/common";

import { billingTargetTypes } from "../../../common/constants";

import BaseFilterContainer from "./BaseFilter";

class ServicesGroupFilterContainer extends Component {
  constructor(props) {
    super();
    this.toggleFilterItem = this.toggleFilterItem.bind(this);
  }

  toggleFilterItem(groupID) {
    if (this.props.selectedTargetType !== this.props.currentTargetType) {
      // add to target_ids and set new target type (old action)
      this.props.selectTarget(groupID);
    } else {
      if (!this.props.selectedTargetIDs.includes(groupID)) {
        // add id to targetIDs
        this.props.selectGroup(groupID);
      } else {
        // cancel unSelecting last targetID,
        // because server will return bad request
        // need to set targetType equals "all"
        // TODO: Set targeType all
        if (this.props.selectedTargetIDs.length !== 1) {
          // remove from target_ids
          this.props.unSelectGroup(groupID);
        }
      }
    }
  }

  render() {
    return (
      <BaseFilterContainer
        allItems={this.props.allItems}
        visibleItems={this.props.visibleItems}
        pageNumber={this.props.pageNumber}
        currentTargetType={this.props.currentTargetType}
        selectedTargetType={this.props.selectedTargetType}
        selectedTargetIDs={this.props.selectedTargetIDs}
        blockTitle={this.props.blockTitle}
        selectTarget={this.toggleFilterItem}
        multiselect={true}
        selectedItems={this.props.selectedItems}
        hideIcon={true}
      />
    );
  }
}

const mapStateToProps = state => {
  let [selectedGroups, unSelectedGroups] = separateSelectedItems(
    state.billing.filters.hierarchy.servicesGroups,
    state.billing.filters.selections.servicesGroups
  );
  let filteredGroups = getFilteredServicesGroups(
    state.billing.filters.selections,
    unSelectedGroups
  );
  return {
    selectedItems: selectedGroups,
    visibleItems: filteredGroups, // paginator
    currentTargetType: billingTargetTypes.group,
    selectedTargetType: state.billing.options.targetType,
    selectedTargetIDs: state.billing.options.targetIDs,
    blockTitle: "Services Groups"
  };
};

const mapDispatchToProps = dispatch => ({
  selectGroup: groupID => {
    dispatch(addGroupToTargetIDs(groupID));
  },
  unSelectGroup: groupID => {
    dispatch(removeGroupFromTargetIDs(groupID));
  },
  selectTarget: targetID => {
    dispatch(setTargetOption(targetID, billingTargetTypes.group));
  }
});

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ServicesGroupFilterContainer);
