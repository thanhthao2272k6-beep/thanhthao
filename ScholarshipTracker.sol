
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ScholarshipTracker {

    address public administrator;

    enum Status {
        Pending,
        Accepted,
        Rejected
    }

    struct Application {
        string applicationRef;
        Status status;
        uint256 submittedAt;
    }

    mapping(address => Application) public applications;
    mapping(bytes32 => address) public applicationRefOwners;

    event ApplicationSubmitted(
        address indexed applicant,
        string applicationRef,
        uint256 submittedAt
    );

    event ApplicationDecision(
        address indexed applicant,
        string applicationRef,
        Status decision,
        address indexed administrator
    );

    modifier onlyAdministrator() {
        require(
            msg.sender == administrator,
            "Only administrator can perform this action"
        );
        _;
    }

    constructor() {
        administrator = msg.sender;
    }

    function submitApplication(
        string memory _applicationRef
    ) public {
        require(
            bytes(_applicationRef).length > 0,
            "Reference cannot be empty"
        );

        require(
            bytes(applications[msg.sender].applicationRef).length == 0,
            "Applicant already submitted an application"
        );

        bytes32 refHash = keccak256(bytes(_applicationRef));

        require(
            applicationRefOwners[refHash] == address(0),
            "Application reference already exists"
        );

        applications[msg.sender] = Application({
            applicationRef: _applicationRef,
            status: Status.Pending,
            submittedAt: block.timestamp
        });

        applicationRefOwners[refHash] = msg.sender;

        emit ApplicationSubmitted(
            msg.sender,
            _applicationRef,
            block.timestamp
        );
    }

    function acceptApplication(
        address _applicant
    ) public onlyAdministrator {
        require(
            bytes(applications[_applicant].applicationRef).length > 0,
            "Application does not exist"
        );

        require(
            applications[_applicant].status == Status.Pending,
            "Application is not pending"
        );

        applications[_applicant].status = Status.Accepted;

        emit ApplicationDecision(
            _applicant,
            applications[_applicant].applicationRef,
            Status.Accepted,
            msg.sender
        );
    }

    function rejectApplication(
        address _applicant
    ) public onlyAdministrator {
        require(
            bytes(applications[_applicant].applicationRef).length > 0,
            "Application does not exist"
        );

        require(
            applications[_applicant].status == Status.Pending,
            "Application is not pending"
        );

        applications[_applicant].status = Status.Rejected;

        emit ApplicationDecision(
            _applicant,
            applications[_applicant].applicationRef,
            Status.Rejected,
            msg.sender
        );
    }

    function getApplication(
        address _applicant
    )
        public
        view
        returns (
            string memory applicationRef,
            Status status,
            uint256 submittedAt
        )
    {
        require(
            bytes(applications[_applicant].applicationRef).length > 0,
            "Application does not exist"
        );

        Application memory app = applications[_applicant];

        return (
            app.applicationRef,
            app.status,
            app.submittedAt
        );
    }
}
