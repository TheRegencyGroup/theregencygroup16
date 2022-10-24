/** @odoo-module **/

const { Component, useState } = owl;

const MAX_PAGE_NUMBERS = 7;
const PAGE_OFFSET = 2;

export class ListPagination extends Component {
    setup() {
        this.PREV_PAGE = 'prev';
        this.NEXT_PAGE = 'next';

        this.state = useState({
            maxPageNumbers: MAX_PAGE_NUMBERS,
            pageOffset: PAGE_OFFSET,
        });
    }

    get numberOfPages() {
        let total = this.props.totalItemsNumber;
        let limit = this.props.listLimit;
        let numberOfPages = Math.floor(total / limit);
        if (total % limit > 0) {
            numberOfPages++;
        }
        return numberOfPages;
    }

    get leftPages() {
        let pages = [1];
        if (this.props.currentPage <= this.state.pageOffset * 2) {
            pages = this.arrayFromRange(1, this.props.currentPage + this.state.pageOffset);
        }
        return pages;
    }

    get centerPages() {
        let pages = false;
        if (this.props.currentPage > this.state.pageOffset * 2 && this.props.currentPage <= this.numberOfPages - this.state.pageOffset * 2) {
            pages = this.arrayFromRange(this.props.currentPage - this.state.pageOffset, this.props.currentPage + this.state.pageOffset);
        }
        return pages;
    }

    get rightPages() {
        let pages = [this.numberOfPages];
        if (this.props.currentPage > this.numberOfPages - this.state.pageOffset * 2) {
            pages = this.arrayFromRange(this.props.currentPage - this.state.pageOffset, this.numberOfPages);
        }
        return pages;
    }

    arrayFromRange (min, max) {
        return Array.from({ length: max - min + 1 },(a,e) => e + min);
    }

    onClickPageBtn(pageNumber) {
        let page;
        if (pageNumber === this.PREV_PAGE) {
            page = this.props.currentPage - 1;
        } else if (pageNumber === this.NEXT_PAGE) {
            page = this.props.currentPage + 1;
        } else {
            page = pageNumber;
        }
        if (!page || page === this.props.currentPage || page < 1 || page > this.numberOfPages) {
            return;
        }
        this.props.changePage(page)
    }
}

ListPagination.props = {
    totalItemsNumber: Number,
    listLimit: Number,
    currentPage: Number,
    changePage: Function,
}

ListPagination.template = 'list_pagination';
