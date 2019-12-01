import React from 'react';
import './App.css';

function ConversationPill(props) {
  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5 className="">{props.group_name}</h5>
        <div className="">{props.message_count} messages</div>
        <div className="text-muted small"><ul className="participants">{props.participants ? props.participants.map((name) => <li>{name}</li>) : "No participants"}</ul></div>
      </div>
    </div>
  );
}

class ConversationList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      items: []
    };
  }

  componentDidMount() {
    fetch("http://localhost:5000/api/conversations")
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            items: result.conversations
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    const { error, isLoaded, items } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return (
        <div class="text-center">
          <div class="spinner-border" role="status">
            <span class="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
      return (
          items.map(item => (
            <ConversationPill group_name={item.groupName} message_count={item.count} participants={item.participant} />
          ))
      );
    }
  }
}

function App() {
  return (
    <div>
    <div className="container">
      <div className="row">
        <div className="col-12">
          <div className="hero mt-3 mb-3 text-center">
            <h1 className="display-4 font-weight-light">converscope</h1>
            <p class="lead font-italic">daylen's texts, 2009-2019</p>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-12">
        <div class="btn-toolbar mb-3">
          <div class="btn-group">
            <button type="button" class="btn btn-primary active">DMs</button>
            <button type="button" class="btn btn-primary">Groups</button>
          </div>
        </div>
        <ConversationList />
        </div>
      </div>
    </div>
    </div>
  );
}

export default App;
