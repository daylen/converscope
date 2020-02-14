import React from 'react';
import { BrowserRouter as Router, Switch, Route, Link} from 'react-router-dom';
import * as constants from './constants.js';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar';
import Button from 'react-bootstrap/Button';

function metric_pretty_name(metric_short_name) {
  return metric_short_name.replace(/_/g, ' ');
}

function MetricRow(props) {
  return (
    <div>
    <hr />
    <h5 className="small-caps">{metric_pretty_name(props.metric_name)}</h5>
    <div class="row">{props.values.map((arr) =>
      <div className="statistic col-sm-4"><div className="big-number">{arr[1].toLocaleString()}</div><div className="small">{arr[0]}</div></div>)}</div>
    </div>
  )
}

function DetailCommandBar(props) {
  return (
    <div>
    <ButtonToolbar>
    <Link to="/"><Button variant="warning">Back to list</Button></Link>
    </ButtonToolbar>
    <hr />
    </div>
  );
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
    } else {
      return (
        <div>
          {this.state.isLoaded ? 
            <div>
            <div className="text-danger clip">{this.props.c_id}</div>
            <h4>{this.state.groupName}</h4>
            <div className="text-muted small">
              <ul className="participants">{this.state.participants.length > 0 ? this.state.participants.map((name) => <li key={this.state.c_id + name}>{name}</li>) : ""}</ul>
            </div>
            <div>
            {Object.entries(this.state.metrics).map(([key, value]) => <MetricRow metric_name={key} values={value} />)}
            </div></div>
          : <div className="text-center">
              <div className="spinner-border" role="status">
                <span className="sr-only">Loading...</span>
              </div>
            </div>}
        </div>
      );
    }
  }
}

export default DetailPage;