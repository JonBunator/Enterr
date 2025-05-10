import { Chip } from "@mui/material";
import { ActionStatusCode } from "../../../api/apiModels.ts";
import './Triggers.scss';
import { ArrowPathIcon, CheckIcon, XMarkIcon } from "@heroicons/react/24/solid";

export interface TriggersProps {
  triggers: ActionStatusCode[]
}

export default function Triggers(props: TriggersProps) {

  const { triggers } = props;

  function getLabel(trigger: ActionStatusCode) {
    if (trigger === 'SUCCESS') {
      return 'Success'
    }
    else if (trigger === 'FAILED') {
      return 'Failed'
    }
    else if (trigger === 'IN_PROGRESS') {
      return 'In Progress'
    }
    return '';
  }

  function getIcon(trigger: ActionStatusCode) {
    if (trigger === 'SUCCESS') {
      return <CheckIcon className="icon"/>
    } else if (trigger === 'FAILED') {
      return <XMarkIcon className="icon"/>
    } else if (trigger === 'IN_PROGRESS') {
      return <ArrowPathIcon className="icon"/>
    }
  }

  function getColor(trigger: ActionStatusCode) {
    if (trigger === 'SUCCESS') {
      return 'success'
    }
    else if (trigger === 'FAILED') {
      return 'error'
    }
    else if (trigger === 'IN_PROGRESS') {
      return 'running'
    }
  }

  return (
    <div className="trigger">
      {triggers.map((trigger) => <Chip icon={getIcon(trigger)}  label={getLabel(trigger)} className={getColor(trigger)} key={trigger} />)}
    </div>
  );
}