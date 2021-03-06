import React, { Component } from "react";

import { FilterBlockComponent } from "../components/filterBlock";
import { paginator } from "../../../common/paginator";

class FilterContainer extends Component {
  constructor(props) {
    super();
    this.state = {
      pageNumber: 1,
      searchQuery: ""
    };
    this.onSearchInputChange = this.onSearchInputChange.bind(this);
    this.checkIsTargetSelected = this.checkIsTargetSelected.bind(this);
    this.setPageNumber = this.setPageNumber.bind(this);
  }

  onSearchInputChange(event) {
    const searchQuery = event.target.value;
    this.setState({ searchQuery });
  }

  checkIsTargetSelected(targetID) {
    if (this.props.currentTargetType === this.props.selectedTargetType) {
      return targetID === this.props.selectedTargetID;
    }
  }

  setPageNumber(pageNumber) {
    this.setState({ pageNumber });
  }

  render() {
    let visibleItems;
    if (this.state.searchQuery) {
      visibleItems = this.props.visibleItems.filter(item =>
        item.title.includes(this.state.searchQuery)
      );
    } else visibleItems = this.props.visibleItems;

    let page = paginator(visibleItems).getPage(this.state.pageNumber);

    return (
      <FilterBlockComponent
        page={page}
        setPageNumber={this.setPageNumber}
        hideCheckbox={this.props.hideCheckbox}
        selectedItems={this.props.selectedItems}
        onSelectFilterItem={this.props.selectFilterItem}
        onUnselectFilterItem={this.props.unSelectFilterItem}
        onSearchInputChange={this.onSearchInputChange}
        blockTitle={this.props.blockTitle}
        blockTitleIconClass={this.props.blockTitleIconClass}
        onItemClick={this.props.selectTarget}
        checkIsTargetSelected={this.checkIsTargetSelected}
        loading={this.props.loading}
        error={this.props.error}
      />
    );
  }
}

export default FilterContainer;
