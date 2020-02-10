import React from 'react';
import { BrowserRouter as Router, Switch, Route, Link, useParams } from 'react-router-dom';
import * as constants from './constants.js';

function metric_pretty_name(metric_short_name) {
	if (metric_short_name == 'chars_sent') {
		return 'Characters Sent';
	}
	if (metric_short_name == 'messages_sent') {
		return 'Messages Sent';
	}
}

function MetricRow(props) {
	return (
		<div>
		<h5 className="small-caps">{metric_pretty_name(props.metric_name)}</h5>
		<div class="row">{Object.entries(props.values).map(([key, value]) =>
			<div className="statistic col-sm-4"><div className="big-number">{value.toLocaleString()}</div><div className="small">{key}</div></div>)}</div>
		<hr />
		</div>
	)
}

class DetailPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      groupName: '',
      metrics: {},
      participants: [],
    };
  }

  foo = (forced) => {
  	let url = constants.URL_PREFIX + "/api/conversation?id=" + this.props.c_id;
  	console.log(url);
    fetch(url)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            groupName: result.groupName,
            metrics: result.metrics,
            participants: result.participant,
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            isLoaded: true,
            error: error,
          });
        }
      )
  }

  componentDidMount() {
    this.foo(true);
  }

  render() {
    if (this.state.error) {
      return <div>Error: {this.state.error.message}</div>;
    } else if (!this.state.isLoaded) {
      return (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
      return (
        <div>
        	<h4>{this.state.groupName}</h4>
        	<div className="text-muted small">
          		<ul className="participants">{this.state.participants.length > 0 ? this.state.participants.map((name) => <li key={this.state.c_id + name}>{name}</li>) : ""}</ul>
          	</div>
          	<div>
          	{Object.entries(this.state.metrics).map(([key, value]) => <MetricRow metric_name={key} values={value} />)}
          	</div>
        </div>
      );
    }
  }
}

export default DetailPage;