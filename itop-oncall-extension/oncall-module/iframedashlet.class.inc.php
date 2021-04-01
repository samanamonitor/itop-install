<?php
class DashletIFrame extends Dashlet
{
  public function __construct($oModelReflection, $sId)
  {
    parent::__construct($oModelReflection, $sId);
  }

  static public function GetInfo()
  {
    return array(
      'label' => Dict::S('UI:DashletIframe:OnCall'),
      'icon' => 'env-'.utils::GetCurrentEnvironment().'/oncall-module/images/calendar-icon.png',
      'description' => Dict::S('UI:DashletIframe:Description'),
    );
  }

  public function GetPropertiesFields(DesignerForm $oForm)
  {
    
  }

  public function Render($oPage, $bEditMode = false, $aExtraParams = array())
  {
    $oPage->add_header('<script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.5.1/main.min.js"></script>');
    $oPage->add_header('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/fullcalendar@5.5.1/main.min.css">');

    $sId = utils::GetSafeId('dashlet_iframe_'.($bEditMode? 'edit_' : '').$this->sId);
    $oPage->add_script('
    <script>
      document.addEventListener("DOMContentLoaded", function() {
        var calendarEl = document.getElementById("'.$sId.'");
        var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth"
        });
        calendar.render();
      });
    </script>
    ');

    $oPage->add('<div class="dashlet-content">');

    $oPage->add('<div id='.$sId.'></div>');

    if($bEditMode)
    {
      $oPage->add('<div style="width: 100%; height: 100%; position: absolute; top: 0px; left: 0px; cursor: not-allowed;"></div>');
    }

    $oPage->add('</div>');
  }
}