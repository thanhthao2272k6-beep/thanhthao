// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ScholarshipApplicationTracker {
    enum Decision {
        Pending,
        Accepted,
        Rejected
    }

    struct Application {
        address applicant;
        bytes32 referenceHash;
        Decision decision;
    }

    address public immutable administrator;
    Application[] private applications;
    mapping(address => uint256) private applicationIndexPlusOne;
    mapping(bytes32 => address) private referenceApplicant;

    event ApplicationSubmitted(address indexed applicant, bytes32 indexed referenceHash);
    event ApplicationDecided(address indexed applicant, Decision decision, address indexed administrator);

    error NotAdministrator();
    error EmptyReference();
    error AlreadyApplied();
    error ReferenceAlreadyUsed();
    error ApplicationNotFound();
    error ApplicationAlreadyDecided();
    error InvalidDecision();

    constructor() {
        administrator = msg.sender;
    }

    function submitApplication(bytes32 referenceHash) external {
        if (referenceHash == bytes32(0)) revert EmptyReference();
        if (applicationIndexPlusOne[msg.sender] != 0) revert AlreadyApplied();
        if (referenceApplicant[referenceHash] != address(0)) revert ReferenceAlreadyUsed();

        applications.push(Application(msg.sender, referenceHash, Decision.Pending));
        applicationIndexPlusOne[msg.sender] = applications.length;
        referenceApplicant[referenceHash] = msg.sender;
        emit ApplicationSubmitted(msg.sender, referenceHash);
    }

    function decideApplication(address applicant, Decision decision) external {
        if (msg.sender != administrator) revert NotAdministrator();
        if (decision != Decision.Accepted && decision != Decision.Rejected) revert InvalidDecision();

        uint256 indexPlusOne = applicationIndexPlusOne[applicant];
        if (indexPlusOne == 0) revert ApplicationNotFound();

        Application storage application = applications[indexPlusOne - 1];
        if (application.decision != Decision.Pending) revert ApplicationAlreadyDecided();

        application.decision = decision;
        emit ApplicationDecided(applicant, decision, msg.sender);
    }

    function getApplicationCount() external view returns (uint256) {
        return applications.length;
    }

    function getApplication(uint256 index) external view returns (Application memory) {
        return applications[index];
    }

    function getApplicantApplication(address applicant) external view returns (Application memory) {
        uint256 indexPlusOne = applicationIndexPlusOne[applicant];
        if (indexPlusOne == 0) revert ApplicationNotFound();
        return applications[indexPlusOne - 1];
    }
}
